#!/bin/bash

#UPDATE `data` SET `status`='%s' WHERE `id`='%s'

# got the csv by running:
#    SELECT `status`, `id`  FROM `data` WHERE `status` NOT IN ("", "deleted", "duplicate", "old") ORDER BY `status` ASC

X="$IFS";
IFS="\n";
ST="`cat ../db/dev-reimportStatuses-output.csv`"
IFS="$X";

for line in $ST; do 
    P=`echo $line|sed 's/","/" "/'`
    CMD=`printf "UPDATE data SET userStatus=%s WHERE id=%s" $P`
    
    sqlite3 -batch -bail "../db/main.sqlite" "$CMD"
    
    echo -en "."
done