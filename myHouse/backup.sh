#!/bin/bash

DT=`date "+%Y-%m-%d %H.%M.%S"`;
DEST="/media/BIG/TEMP/myHouse/$DT/";


BACKUP="default"
CLEANUP=""
while test $# -gt 0; do
    case $1 in
        -gather)
            shift
            GATHER=$1
            ;;
        -cleanup)
            shift
            CLEANUP=$1
            ;;
            
        *)
            echo "Invalid argument: $1"
            exit
            ;;
    esac
    shift
done

echo "size: `du -shc "../db/" | grep -E "total" | sed "s/total//"`"


if [ "$BACKUP" == "default" ]; then
    mkdir "$DEST/";
    mkdir "$DEST/db/";
    cp -fv "../db/"*.sqlite "$DEST/db/"
fi

if [ "$CLEANUP" == "cleanup" ]; then
    for file in `ls -1 "../db/"*.sqlite`; do
        echo "VACUUM $file";
        sqlite3 -batch -bail "$file" "VACUUM" &
    done;
fi



echo "final size: `du -shc "../db/" | grep -E "total" | sed "s/total//"`"