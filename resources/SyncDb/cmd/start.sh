#!/bin/bash
rm -f /var/local/osm_db/osm3s_v0.7.55_osm_base
rm -f /dev/shm/osm3s_v0.7.55_osm_base
/usr/local/bin/dispatcher --osm-base --meta --db-dir=/var/local/osm_db & 
rc=$?
echo $! > ./cmd/pid
exit $rc