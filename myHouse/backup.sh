#!/bin/bash

DT=`date "+%Y-%m-%d %H.%M.%S"`;

DEST="../db-$DT/";

mkdir "$DEST";
cp -fv "../db/"* "$DEST"

