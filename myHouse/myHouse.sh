#!/bin/bash

cd git/myHouse/myHouse/
./update.sh

OUT="/tmp/myHouse.log"
echo "case-noi-metrou" > $OUT
./view.py --profile=case-noi-metrou >> $OUT
echo "" >> $OUT
echo "" >> $OUT
echo "" >> $OUT
echo "case-noi" >> $OUT
./view.py --profile=case-noi >> $OUT


#/view.py --profile=none -age=9999 -agea=9999 -status=todo
#notify/notify.py -user="rassandra21@gmail.com" -message="`cat /tmp/myHouse.log`"

cat $OUT | less

rm $OUT