#!/bin/bash

if [ ! -d "../db/" ]; then 
    mkdir "../db/"
fi

if [ ! -d "../db/locks/" ]; then 
    mkdir "../db/locks/"
fi


LDIR="../db/locks/"

OFILE="/dev/null"

DT=`date +"%Y-%m-%d %H:%M:%S"`
echo "[$DT] updater started"


(
    echo > "$LDIR/anuntul_ro"
    echo "anuntul_ro->case-vile";
    python ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "anuntul_ro" -category "case-vile" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/"               
    
    echo "anuntul_ro->apt-2-cam";
    python ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-2-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/"    
    
    echo "anuntul_ro->apt-3-cam";
    python ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-3-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-1/"     
    
    echo "anuntul_ro->apt-4-cam";
    python ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-4-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-1/"
    
    rm "$LDIR/anuntul_ro"
) 1>&2 >"$OFILE" &



(
    echo > "$LDIR/imobiliare_ro"
    echo "imobiliare_ro->case-vile";
    python ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "case-vile" -url "http://www.imobiliare.ro/vanzare-case-vile/bucuresti"
    
    echo "imobiliare_ro->apt-2-cam";
    python ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "apt-2-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=2"
    
    echo "imobiliare_ro->apt-3-cam";
    python ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "apt-3-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=3"
    
    echo "imobiliare_ro->apt-4-cam";
    python ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "apt-4-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=4"
    
    rm "$LDIR/imobiliare_ro"
) 1>&2 >"$OFILE" &



(
    echo > "$LDIR/tocmai_ro"
    echo "tocmai_ro->case-vile";
    python ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "case-vile" -url "http://www.tocmai.ro/cauta?page=1&typ=1&ct=8&jd=26&tz=1"
    
    echo "tocmai_ro->apt-2-cam";
    python ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "apt-2-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=2&img=1"
    
    echo "tocmai_ro->apt-3-cam";
    python ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "apt-3-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=3&img=1"
    
    echo "tocmai_ro->apt-4-cam";
    python ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "apt-4-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=4&img=1"
    
    rm "$LDIR/tocmai_ro"
) 1>&2 >"$OFILE" &


(
    echo > "$LDIR/mercador_ro"
    echo "mercador_ro->search[vanzare-case]"
    python ./gather.py -v=1 -sleep=0.75 -user-agent="random" -module "mercador_ro" -category "case-vile" -url "http://mercador.ro/imobiliare/case-de-vanzare-si-de-inchiriat/bucuresti/?search[filter_float_price%3Afrom]=20000&search[filter_float_price%3Ato]=90000&search[filter_enum_alege]=vanzare"
    
    rm "$LDIR/mercador_ro"
) 1>&2 >"$OFILE" &



(
    echo > "$LDIR/imopedia_ro"
    echo "imopedia_ro->case-vile"
    python ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "case-vile" -url "http://www.imopedia.ro/bucuresti/vanzari-vile.html"
    
    echo "imopedia_ro->apt-2-cam"
    python ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "apt-2-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-2-camere-1104056-0-pagina-0.html"
    
    echo "imopedia_ro->apt-3-cam"
    python ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "apt-3-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-3-camere-1102874-0-pagina-0.html"
    
    echo "imopedia_ro->apt-4-cam"
    python ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "apt-4-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-4-camere-1104405-0-pagina-0.html"
    
    rm "$LDIR/imopedia_ro"
) 1>&2 >"$OFILE" &

(
    echo > "$LDIR/az_ro"
    echo "az_ro->case-file";
    python ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "case-vile" -url "http://www.az.ro/imobiliare-vanzari/case-vile"
    
    echo "az_ro->apt-2-cam";
    python ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "apt-2-cam" -url "http://www.az.ro/imobiliare-vanzari/2-camere"
    
    echo "az_ro->apt-3-cam";
    python ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "apt-3-cam" -url "http://www.az.ro/imobiliare-vanzari/3-camere"
    
    echo "az_ro->apt-4-cam";
    python ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "apt-4-cam" -url "http://www.az.ro/imobiliare-vanzari/4-camere"
    
    rm "$LDIR/az_ro"
) 1>&2 >"$OFILE" &





LOCKED=1

echo "";
while [ "$LOCKED" ]; do
    LOCKS=`ls -1 "$LDIR" | sort | tr "\\n" " "`
    
    if [ -z "$LOCKS" ]; then
        LOCKED=0;
    fi;
    
    DT=`date +"%Y-%m-%d %H:%M:%S"`
    echo -e -n "\r[$DT] Waiting for $LOCKS to finish            ";
    sleep 1.5
done
echo "";


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


echo "------------------------------------------------------------------------------------";
echo "cleanup";
#python ./cleanup.py -v=5 -vacuum=1
python ./cleanup.py -v=1 -nodescription=1 -fixstatus=1 
#python ./cleanup.py -v=5 -deleteOldItems=1 

