#!/bin/bash

if [ ! -d "../db/" ]; then 
    mkdir "../db/"
    rm cache.sqlite
    mv *.sqlite "../db/"
fi


echo "anuntul_ro->case-vile";
python ./gather.py -v=1 -sleepo=0.1 -user-agent="random" -module "anuntul_ro" -category "case-vile" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/"               

#echo "anuntul_ro->apt-2-camere";
#python ./gather.py -v=1 -sleepo=0.1 -user-agent="random" -module "anuntul_ro" -category "apt-2-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/"    

echo "anuntul_ro->apt-3-camere";
python ./gather.py -v=1 -sleepo=0.1 -user-agent="random" -module "anuntul_ro" -category "apt-3-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-1/"     

echo "anuntul_ro->apt-4-camere";
python ./gather.py -v=1 -sleepo=0.1 -user-agent="random" -module "anuntul_ro" -category "apt-4-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-1/"    

echo "imobiliare_ro->case-file";
python ./gather.py -v=1 -sleepo=0 -user-agent="real" -module "imobiliare_ro" -category "case-vile" -url "http://www.imobiliare.ro/vanzare-case-vile/bucuresti"

echo "tocmai_ro->case-file";
python ./gather.py -v=1 -sleepo=0.1 -user-agent="random" -module "tocmai_ro" -category "case-vile" -url "http://www.tocmai.ro/cauta?page=1&typ=1&ct=8&jd=26&tz=1"

echo "az_ro->case-file";
python ./gather.py -v=1 -sleepo=0.1 -user-agent="random" -module "az_ro" -category "case-vile" -url "http://www.az.ro/imobiliare-vanzari/case-vile"




echo "anuntul_ro->process";
python ./process.py -v=1 -module "anuntul_ro"

echo "imobiliare_ro->process";
python ./process.py -v=1 -module "imobiliare_ro"

echo "tocmai_ro->process";
python ./process.py -v=1 -module "tocmai_ro"

echo "az_ro->process";
python ./process.py -v=1 -module "az_ro"
