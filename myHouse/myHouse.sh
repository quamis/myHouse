#!/bin/bash

cd "$HOME/git/myHouse/myHouse/"

UPDATE="default"
SYNCREMOTE="default"
CLEANUP="default" # thorough

SYNC_SOURCEURL=""
SYNC_FTP_HOST=""
SYNC_FTP_USER=""
SYNC_FTP_PASS=""
SYNC_FTP_PATH=""


source "$HOME/.myHouse.cfg"

while test $# -gt 0; do
    case $1 in
        -update)
            shift
            UPDATE=$1
            ;;
        -cleanup)
            shift
            CLEANUP=$1
            ;;
        -syncRemote)
            shift
            SYNCREMOTE=$1
            ;;
        *)
            echo "Invalid argument: $1"
            exit
            ;;
    esac
    shift
done


#######################################################################################################
OUTDIR="/tmp/myHouse/"
if [ ! -d "$OUTDIR" ]; then
    mkdir "$OUTDIR"
fi;

if [ "$UPDATE" == "default" ]; then
    ./update.sh -cleanup "$CLEANUP"
fi;

if [ "$SYNCREMOTE" == "default" -o "$SYNCREMOTE" == "local" ]; then
    wget --quiet "$SYNC_SOURCEURL" -O "$OUTDIR/localStatuses.json"
    STATUSES=`cat "$OUTDIR/localStatuses.json"| json_pp -f json -t json | grep -P '"([^\"]+)" : "([^\"]+)"' | sed -r 's/"([^\"]+)" : "([^\"]+)"(,)?/-id="\1" --newStatus="\2"/g' `
    while read -r line; do
        if [ -n "$line" ]; then
            CMD="./view.py $line"
            echo $CMD
            eval "$CMD"
        fi;
    done <<< "$STATUSES"
    echo "{ }"> "$OUTDIR/localStatuses.json"
    
    
    echo "Computing suggestions lists"
    ./view.py -category="case-vile" -status="todo%" --outputFormat="id" > /tmp/TODO.json
    ./view.py -category="case-vile" -status="hide%" --outputFormat="id" > /tmp/HIDE.json
    ./view.py -category="case-vile" -status=""     --outputFormat="id" > /tmp/TEST.json
    ./suggestions.py -datasetHIDE="/tmp/HIDE.json" -datasetTODO="/tmp/TODO.json" -datasetTEST="/tmp/TEST.json" -train=1 --outputFormat=json > /tmp/suggestions.json
    #./import.py -jsonFile=/tmp/suggestions.json -targetField=suggestedStatus > /tmp/import-suggestions.json
fi;


if [ "$SYNCREMOTE" == "default" ]; then
    ./view.py --profile=case-valide --outputFormat="html-php" >   "$OUTDIR/profile.case-vile.json"
    ./view.py -category="apt-2-cam" -maxPrice=70000 -minPrice=30000 -ageu=1.5 --outputFormat="html-php" >   "$OUTDIR/profile.apt-2-cam.json"
    ./view.py -category="apt-3-cam" -maxPrice=70000 -minPrice=30000 -ageu=1.5 --outputFormat="html-php" >   "$OUTDIR/profile.apt-3-cam.json"
    ./view.py -category="apt-4-cam" -maxPrice=70000 -minPrice=30000 -ageu=1.5 --outputFormat="html-php" >   "$OUTDIR/profile.apt-4-cam.json"
        
    notify/notify-ftp.py -host="$SYNC_FTP_HOST" -username="$SYNC_FTP_USER" -password="$SYNC_FTP_PASS" -remotePath="$SYNC_FTP_PATH" \
        -attach="$OUTDIR/profile.case-vile.json" \
        -attach="$OUTDIR/profile.apt-2-cam.json" \
        -attach="$OUTDIR/profile.apt-3-cam.json" \
        -attach="$OUTDIR/profile.apt-4-cam.json" \
        -attach="$OUTDIR/localStatuses.json" \

fi



./graph.py -category=case-vile -price_min=30000 -price_max=70000 -interval_max=30
