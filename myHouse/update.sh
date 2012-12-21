#!/bin/bash

if [ ! -d "../db/" ]; then 
    mkdir "../db/"
    rm cache.sqlite
    mv *.sqlite "../db/"
fi


echo "anuntul_ro->case-vile";
python ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "anuntul_ro" -category "case-vile" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/"               

echo "anuntul_ro->apt-2-camere";
python ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-2-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/"    

echo "anuntul_ro->apt-3-camere";
python ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-3-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-1/"     

echo "anuntul_ro->apt-4-camere";
python ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-4-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-1/"    

echo "imobiliare_ro->case-vile";
python ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "case-vile" -url "http://www.imobiliare.ro/vanzare-case-vile/bucuresti"

echo "tocmai_ro->case-vile";
python ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "case-vile" -url "http://www.tocmai.ro/cauta?page=1&typ=1&ct=8&jd=26&tz=1"

echo "az_ro->case-file";
python ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "case-vile" -url "http://www.az.ro/imobiliare-vanzari/case-vile"

echo "mercador_ro->search[vanzare-case]"
python ./gather.py -v=1 -sleep=0.75 -user-agent="random" -module "mercador_ro" -category "case-vile" -url "http://mercador.ro/imobiliare/case-de-vanzare-si-de-inchiriat/bucuresti/?search[filter_float_price%3Afrom]=20000&search[filter_float_price%3Ato]=90000&search[filter_enum_alege]=vanzare"

echo "imopedia_ro->case-vile"
python ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "case-vile" -url "http://www.imopedia.ro/bucuresti/vanzari-vile.html"



echo "anuntul_ro->process";
python ./process.py -v=1 -module "anuntul_ro"

echo "imobiliare_ro->process";
python ./process.py -v=1 -module "imobiliare_ro"

echo "tocmai_ro->process";
python ./process.py -v=1 -module "tocmai_ro"

echo "az_ro->process";
python ./process.py -v=1 -module "az_ro"

echo "mercador_ro->process";
python ./process.py -v=1 -module "mercador_ro"

echo "imopedia_ro->process";
python ./process.py -v=1 -module "imopedia_ro"

echo "cleanup";
python ./cleanup.py -v=5 -vacuum=1
#python ./cleanup.py -v=1 -nodescription=1 -fixstatus=1 
#python ./cleanup.py -v=5 -deleteOldItems=1 

