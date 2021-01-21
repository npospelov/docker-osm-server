#!/bin/bash
if [ -e ./cmd/pid ]
then
 echo stopping process `cat ./cmd/pid`
 kill -9 `cat ./cmd/pid`
 rm -f /var/local/osm_db/osm3s_v0.7.55_osm_base
 rm -f /dev/shm/osm3s_v0.7.55_osm_base
 rm -f pid
else
 echo "no pid file found!"
 exit 1
fi

exit 0