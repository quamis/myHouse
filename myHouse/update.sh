#!/bin/bash

if [ ! -d "../db/" ]; then 
    mkdir "../db/"
fi

if [ ! -d "../db/locks/" ]; then 
    mkdir "../db/locks/"
fi

function do_lock(){
    SYS=$1
    DATA=$2
    echo "$DATA" > "$LDIR/$SYS"
}

function do_unlock(){
    SYS=$1
    rm "$LDIR/$SYS"
}

LDIR="../db/locks/"

OFILE="/dev/null"

DT=`date +"%Y-%m-%d %H:%M:%S"`
echo "[$DT] updater started"


function gather_anuntul_ro(){
    do_lock "anuntul_ro" "case-vile"
    ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "anuntul_ro" -category "case-vile" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/"               
    
    do_lock "anuntul_ro" "apt-2-cam"
    ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-2-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/"    
    
    do_lock "anuntul_ro" "apt-3-cam"
    ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-3-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-1/"     
    
    do_lock "anuntul_ro" "apt-4-cam"
    ./gather.py -v=1 -sleep=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-4-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-1/"
    
    do_unlock "anuntul_ro"
}


function gather_imobiliare_ro(){
    do_lock "imobiliare_ro" "case-vile"
    ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "case-vile" -url "http://www.imobiliare.ro/vanzare-case-vile/bucuresti"
    
    do_lock "imobiliare_ro" "apt-2-cam"
    ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "apt-2-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=2"
    
    do_lock "imobiliare_ro" "apt-3-cam"
    ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "apt-3-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=3"
    
    do_lock "imobiliare_ro" "apt-2-cam"
    ./gather.py -v=1 -sleep=0.5 -user-agent="real" -module "imobiliare_ro" -category "apt-4-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=4"
    
    do_unlock "imobiliare_ro"
}


function gather_tocmai_ro(){
    do_lock "tocmai_ro" "case-vile"
    ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "case-vile" -url "http://www.tocmai.ro/cauta?page=1&typ=1&ct=8&jd=26&tz=1"
    
    do_lock "tocmai_ro" "apt-2-cam"
    ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "apt-2-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=2&img=1"
    
    do_lock "tocmai_ro" "apt-2-cam"
    ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "apt-3-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=3&img=1"
    
    do_lock "tocmai_ro" "apt-2-cam"
    ./gather.py -v=1 -sleep=0.0 -user-agent="random" -module "tocmai_ro" -category "apt-4-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=4&img=1"
    
    do_unlock "tocmai_ro"
}


function gather_mercador_ro(){
    do_lock "mercador_ro" "case-vile(limited-search)"
    ./gather.py -v=1 -sleep=0.75 -user-agent="random" -module "mercador_ro" -category "case-vile" -url "http://mercador.ro/imobiliare/case-de-vanzare-si-de-inchiriat/bucuresti/?search[filter_float_price%3Afrom]=20000&search[filter_float_price%3Ato]=90000&search[filter_enum_alege]=vanzare"
    
    do_unlock "mercador_ro"
}


function gather_imopedia_ro(){
    do_lock "imopedia_ro" "case-vile"
    ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "case-vile" -url "http://www.imopedia.ro/bucuresti/vanzari-vile.html"
    
    do_lock "imopedia_ro" "apt-2-cam"
    ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "apt-2-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-2-camere-1104056-0-pagina-0.html"
    
    do_lock "imopedia_ro" "apt-3-cam"
    ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "apt-3-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-3-camere-1102874-0-pagina-0.html"
    
    do_lock "imopedia_ro" "apt-4-cam"
    ./gather.py -v=1 -sleep=1.5 -user-agent="random" -module "imopedia_ro" -category "apt-4-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-4-camere-1104405-0-pagina-0.html"
    
    do_unlock "imopedia_ro"
}


function gather_az_ro(){
    do_lock "az_ro" "case-vile"
    ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "case-vile" -url "http://www.az.ro/imobiliare-vanzari/case-vile"
    
    do_lock "az_ro" "apt-2-cam"
    ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "apt-2-cam" -url "http://www.az.ro/imobiliare-vanzari/2-camere"
    
    do_lock "az_ro" "apt-3-cam"
    ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "apt-3-cam" -url "http://www.az.ro/imobiliare-vanzari/3-camere"
    
    do_lock "az_ro" "apt-4-cam"
    ./gather.py -v=1 -sleep=1.0 -user-agent="random" -module "az_ro" -category "apt-4-cam" -url "http://www.az.ro/imobiliare-vanzari/4-camere"
    
    do_unlock "az_ro"
}



GATHER="default"
PROCESS="default"
CLEANUP="default"
while test $# -gt 0; do
    case $1 in
        -gather)
            shift
            GATHER=$1
            ;;
        -process)
            shift
            PROCESS=$1
            ;;
        -cleanup)
            shift
            CLEANUP=$1
            ;;
        *)
            echo "Invalid argument: $1"
            ;;
    esac
    shift
done

if [ "$GATHER" == "default" -o "$GATHER" == "linear" ]; then
    # Starting background processes
    if [ "$GATHER" == "linear" ]; then
        echo "Starting linear processes"
        gather_anuntul_ro
        gather_imobiliare_ro
        gather_tocmai_ro
        gather_mercador_ro
        gather_imopedia_ro
        gather_az_ro
    else
        echo "Starting background processes"
        gather_anuntul_ro 1>&2 >"$OFILE" &
        gather_imobiliare_ro 1>&2 >"$OFILE" &
        gather_tocmai_ro 1>&2 >"$OFILE" &
        gather_mercador_ro 1>&2 >"$OFILE" &
        gather_imopedia_ro 1>&2 >"$OFILE" &
        gather_az_ro 1>&2 >"$OFILE" &
    fi;
    
    
    LOCKSC=99999
    while [ $LOCKSC -gt 0 ]; do
        LOCKS=`ls -1 "$LDIR" | sort`
        LOCKSC=`ls -1 "$LDIR" | wc -l`
    
        if [ $LOCKSC -gt 0 ]; then    
            LOCKSSTR=""
            S=""
            for L in $LOCKS; do
                LOCKSSTR="$LOCKSSTR$S$L(`cat $LDIR/$L`)"
                S=", "
            done
            
            DT=`date +"%Y-%m-%d %H:%M:%S"`
            
            COLS=`tput cols`
            printf "\r%- ${COLS}s" "[$DT] Waiting for $LOCKSSTR to finish";
            sleep 1.5
        fi;
    done
    echo "";
fi;


if [ "$PROCESS" == "default" ]; then
    ./process.py -v=1 -module "anuntul_ro"
    ./process.py -v=1 -module "imobiliare_ro"
    ./process.py -v=1 -module "tocmai_ro"
    ./process.py -v=1 -module "az_ro"
    ./process.py -v=1 -module "mercador_ro"
    ./process.py -v=1 -module "imopedia_ro"
fi;



if [ "$CLEANUP" == "default" ]; then
    echo "cleanup";
    #./cleanup.py -v=5 -vacuum=1
    ./cleanup.py -v=1 -nodescription=1 -fixstatus=1 
    #./cleanup.py -v=5 -deleteOldItems=1 
    
    ./cleanup.py -module="anuntul_ro"
    ./cleanup.py -module="imobiliare_ro"
    ./cleanup.py -module="tocmai_ro"
    ./cleanup.py -module="az_ro"
    ./cleanup.py -module="mercador_ro"
    ./cleanup.py -module="imopedia_ro"
fi

