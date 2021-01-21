#!/bin/bash
echo $1
if [ -e ./osc/$1 ]
then
 /usr/local/bin/update_database --db-dir=/var/local/osm_db < ./osc/$1
 exit $?
else
 echo "file ./osc/$1 not found"
 exit 1
fi

exit 1