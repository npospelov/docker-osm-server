#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER osm;
    CREATE DATABASE gis ENCODING=UTF8;
    GRANT ALL PRIVILEGES ON DATABASE gis TO osm;

EOSQL

psql -c "CREATE EXTENSION hstore;" -d gis;
psql -c "CREATE EXTENSION postgis;" -d gis;

psql -f /home/osm/gis.sql -d gis;

