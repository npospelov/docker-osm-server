#! /bin/sh

su postgres -c "pg_ctl initdb -D /var/lib/postgresql/data"
su postgres -c "pg_ctl -D /var/lib/postgresql/data start"
su postgres -c "sh /docker-entrypoint-initdb.d/init-user-db.sh"

/etc/init.d/renderd start

service cron reload

nohup /usr/local/bin/dispatcher --osm-base --meta --db-dir=/var/local/osm_db &
#nohup /usr/local/bin/dispatcher --areas --db-dir=/var/local/osm_db &
#chmod 666 /var/local/osm_db/osm3s_v0.7.*_areas

service cron start

apache2ctl -D FOREGROUND

