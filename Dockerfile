from postgres

#VOLUME /resources

RUN apt-get -y update \
    && apt-get -y install apache2 apache2-dev autoconf build-essential bundler bzip2 cron curl gdal-bin \
       git-core fonts-noto-cjk fonts-noto-hinted fonts-noto-unhinted imagemagick \
       libarchive-dev libbz2-dev libgd-dev libffi-dev libiniparser-dev libmagickwand-dev libmapnik-dev \
       libpq-dev libruby libsasl2-dev libtool libxml2-dev libxslt1-dev mapnik-utils \
       nodejs npm osmosis postgresql-13-postgis-3 postgresql-server-dev-all python3 python3-pip ruby ruby-dev ssh ttf-unifont unzip yarnpkg

RUN npm install -g carto
RUN pip3 install configparser lxml requests
RUN gem install bundler

RUN adduser osm --gecos "First Last,RoomNumber,WorkPhone,HomePhone" --disabled-password

RUN mkdir /app

COPY resources/libiniparser.conf /etc/ld.so.conf.d
RUN ldconfig

COPY resources/bin/mod_tile.tar.gz /app/
RUN tar -xvzf /app/mod_tile.tar.gz -C /app/; rm -f /app/mod_tile.tar.gz
RUN cd /app/mod_tile/; sh ./autogen.sh; ./configure; make; make install; make install-mod_tile

COPY /resources/bin/openstreetmap-carto-2.41.0.tar.gz /app/

RUN su - osm
RUN tar xvf /app/openstreetmap-carto-2.41.0.tar.gz -C /home/osm
RUN cd /home/osm/openstreetmap-carto-2.41.0; sh ./get-shapefiles.sh; carto project.mml > style.xml
RUN exit

RUN rm -f /app/openstreetmap-carto-2.41.0.tar.gz

COPY resources/renderd.conf /usr/local/etc/
COPY resources/renderd /etc/init.d/
RUN chmod a+x /etc/init.d/renderd

RUN mkdir -p /var/lib/mod_tile; chown osm:osm /var/lib/mod_tile

COPY resources/mod_tile/mod_tile.load /etc/apache2/mods-available/
RUN ln -s /etc/apache2/mods-available/mod_tile.load /etc/apache2/mods-enabled/

COPY resources/apache2/000-default.conf /etc/apache2/sites-enabled/

RUN mkdir /var/www/html/maps

COPY resources/bin/leaflet.zip /var/www/html/maps
RUN cd /var/www/html/maps; unzip leaflet.zip; rm -f leaflet.zip

COPY resources/mod_tile/index.html /var/www/html/maps

##OVERPASS##

RUN mkdir /var/www/html/overpass

COPY resources/bin/osm-3s_v* /app/
RUN tar -xvzf /app/osm-3s_v* -C /home/osm; cd /home/osm/osm-3s_v*; sh ./configure; make install; rm -f /app/osm-3s_v*.tar.gz

RUN cd /home/osm/osm-3s_v*; cp -fr cgi-bin/ /var/www/html/overpass/; cp -fr html/ /var/www/html/overpass/

RUN mkdir /var/local/osm_db; chown osm /var/local/osm_db; chgrp www-data /var/local/osm_db

COPY /resources/bin/piter4.osm.bz2 /app/

RUN su - osm
RUN init_osm3s.sh /app/piter4.osm.bz2 /var/local/osm_db /usr/local --meta
RUN exit

RUN rm -f /app/piter4.osm.bz2

RUN a2enmod cgi

COPY /resources/overpass/overpass.conf /etc/apache2/sites-available
RUN ln -s /etc/apache2/sites-available/overpass.conf /etc/apache2/sites-enabled

#синхронизация БД

COPY /resources/SyncDb /opt/SyncDb

RUN echo "*/1 * * * * /opt/SyncDb/sync_db_run.sh" >> /var/spool/cron/crontabs/root; chmod 600 /var/spool/cron/crontabs/root; chgrp crontab /var/spool/cron/crontabs/root

#OSM

RUN adduser user --gecos "First Last,RoomNumber,WorkPhone,HomePhone" --disabled-password

#RUN cd /home/user; git clone --depth=1 https://github.com/openstreetmap/openstreetmap-website.git; cd openstreetmap-website; bundle update --bundler &&  bundle install

COPY resources/bin/openstreetmap-website.tar.gz /home/user
RUN cd /home/user; tar -xzf openstreetmap-website.tar.gz; rm -f openstreetmap-website.tar.gz; cd openstreetmap-website/; bundle update --bundler &&  bundle install

COPY resources/osm/settings.yml /home/user/openstreetmap-website/config
RUN cd /home/user/openstreetmap-website/db/functions; make libpgosm.so
RUN cd /home/user/openstreetmap-website; touch config/settings.local.yml; cp config/example.database.yml config/database.yml; bundle exec rake yarn:install; chown -R user /home/user/openstreetmap-website; chgrp -R osm /home/user/openstreetmap-website

#финал

COPY /resources/apache2/ports.conf /etc/apache2/

RUN su - osm
COPY resources/db/gis.sql /home/osm
COPY resources/db/openstreetmap.sql /home/osm
RUN exit

RUN su - postgres
COPY ./docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/
RUN exit

COPY resources/user_activation.rb /home/user/openstreetmap-website

COPY /resources/start.sh /app/
CMD ["sh", "/app/start.sh"]

EXPOSE 80 8080 3000
