#!/bin/bash

# update.sh -gather none -process none -cleanup thorough



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

function gather_romino_ro(){
    local SLEEP="1.0"
    local V=5
    local TL1=2
    local TL2=5
    
    do_lock "romino_ro" "case-vile"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "romino_ro" -category "case-vile" -url "http://www.romimo.ro/Case/Casa/vanzare/Bucuresti/Bucuresti/"
    
    local TL1=1
    do_lock "romino_ro" "apt-2-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "romino_ro" -category "apt-2-cam" -url "http://www.romimo.ro/Apartamente/Apartamente-2-camere/vanzare/Bucuresti/Bucuresti/"
    
    do_lock "romino_ro" "apt-3-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "romino_ro" -category "apt-3-cam" -url "http://www.romimo.ro/Apartamente/Apartamente-3-camere/vanzare/Bucuresti/Bucuresti/"
    
    do_lock "romino_ro" "apt-4-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "romino_ro" -category "apt-4-cam" -url "http://www.romimo.ro/Apartamente/Apartamente-4-camere/vanzare/Bucuresti/Bucuresti/"
    
    do_lock "romino_ro" "apt-5-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "romino_ro" -category "apt-4-cam" -url "http://www.romimo.ro/Apartamente/Apartamente-5-camere/vanzare/Bucuresti/Bucuresti/"
    
    do_lock "romino_ro" "apt-6-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "romino_ro" -category "apt-4-cam" -url "http://www.romimo.ro/Apartamente/Apartamente-6-camere/vanzare/Bucuresti/Bucuresti/"
    
    do_unlock "romino_ro"
    
}

function gather_anuntul_ro(){
    local SLEEP="0.75"
    local V=5
    do_lock "anuntul_ro" "case-vile"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "anuntul_ro" -category "case-vile" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/"               
    
    do_lock "anuntul_ro" "apt-2-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "anuntul_ro" -category "apt-2-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/"    
    
    do_lock "anuntul_ro" "apt-3-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "anuntul_ro" -category "apt-3-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-1/"     
    
    do_lock "anuntul_ro" "apt-4-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "anuntul_ro" -category "apt-4-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-1/"
    
    do_unlock "anuntul_ro"
}


function gather_imobiliare_ro(){
    local SLEEP="0.75"
    local V=5
    do_lock "imobiliare_ro" "case-vile"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="real" -module "imobiliare_ro" -category "case-vile" -url "http://www.imobiliare.ro/vanzare-case-vile/bucuresti"
    
    do_lock "imobiliare_ro" "apt-2-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="real" -module "imobiliare_ro" -category "apt-2-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=2"
    
    do_lock "imobiliare_ro" "apt-3-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="real" -module "imobiliare_ro" -category "apt-3-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=3"
    
    do_lock "imobiliare_ro" "apt-4-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="real" -module "imobiliare_ro" -category "apt-4-cam" -url "http://www.imobiliare.ro/vanzare-apartamente/bucuresti?nrcamere=4"
    
    do_unlock "imobiliare_ro"
}


function gather_tocmai_ro(){
    local SLEEP="0.75"
    local V=5
    local TL1=7
    local TL2=10
    
    do_lock "tocmai_ro" "case-vile"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "tocmai_ro" -category "case-vile" -url "http://www.tocmai.ro/cauta?page=1&typ=1&ct=8&jd=26&tz=1"
    
    local TL1=1
    do_lock "tocmai_ro" "apt-2-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "tocmai_ro" -category "apt-2-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=2&img=1"
    
    local TL1=2
    do_lock "tocmai_ro" "apt-3-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "tocmai_ro" -category "apt-3-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=3&img=1"
    
    local TL1=2
    do_lock "tocmai_ro" "apt-4-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "tocmai_ro" -category "apt-4-cam" -url "http://www.tocmai.ro/cauta?typ=1&ct=6&jd=26&tz=1&cm=4&img=1"
    
    do_unlock "tocmai_ro"
}


function gather_mercador_ro(){
    local SLEEP="1.5"
    local V=5
    do_lock "mercador_ro" "case-vile(limited-search)"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "mercador_ro" -category "case-vile" -url "http://mercador.ro/imobiliare/case-de-vanzare/bucuresti/?all_categories=1&search%5Bfilter_float_price%3Afrom%5D=20000&search%5Bfilter_float_price%3Ato%5D=70000&currency=EUR"
    
    do_unlock "mercador_ro"
}


function gather_imopedia_ro(){
    local SLEEP="0.5"
    local V=5
    local TL1=7
    local TL2=10
    do_lock "imopedia_ro" "case-vile"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "imopedia_ro" -category "case-vile" -url "http://www.imopedia.ro/bucuresti/vanzari-vile.html"
    
    TL1=0.5
    do_lock "imopedia_ro" "apt-2-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "imopedia_ro" -category "apt-2-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-2-camere-1104056-0-pagina-0.html"

    TL1=0.9
    do_lock "imopedia_ro" "apt-3-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "imopedia_ro" -category "apt-3-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-3-camere-1102874-0-pagina-0.html"
    
    TL1=0.9
    do_lock "imopedia_ro" "apt-4-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" --timeLimit_gatherLinks="$TL1" --timeLimit_getAll="$TL2" -module "imopedia_ro" -category "apt-4-cam" -url "http://www.imopedia.ro/bucuresti/apartamente-de-vanzare-4-camere-1104405-0-pagina-0.html"
    
    do_unlock "imopedia_ro"
}


function gather_az_ro(){
    local SLEEP="1.5"
    local V=5
    
    do_lock "az_ro" "case-vile"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "az_ro" -category "case-vile" -url "http://www.az.ro/imobiliare-vanzari/case-vile"
    
    do_lock "az_ro" "apt-2-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "az_ro" -category "apt-2-cam" -url "http://www.az.ro/imobiliare-vanzari/2-camere"
    
    do_lock "az_ro" "apt-3-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "az_ro" -category "apt-3-cam" -url "http://www.az.ro/imobiliare-vanzari/3-camere"
    
    do_lock "az_ro" "apt-4-cam"
    ./gather.py -v=$V -sleep=$SLEEP -user-agent="random" -module "az_ro" -category "apt-4-cam" -url "http://www.az.ro/imobiliare-vanzari/4-camere"
    
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
            exit
            ;;
    esac
    shift
done


################################################################################
LDIR="../db/locks/"
OFILE="/tmp/myHouse-update.sh-"
DT=`date +"%Y-%m-%d %H:%M:%S"`
echo "[$DT] updater started"


SOURCES=( "anuntul_ro" "imobiliare_ro" "tocmai_ro" "mercador_ro" "imopedia_ro" "az_ro" "romino_ro" )
#SOURCES=( "az_ro" )
#SOURCES=( "anuntul_ro" )
#SOURCES=( "imopedia_ro" )
#SOURCES=( "tocmai_ro" )


if [ "$GATHER" == "default" -o "$GATHER" == "linear" ]; then
    # Starting background processes
    if [ "$GATHER" == "linear" ]; then
        printf "[`date +"%Y-%m-%d %H:%M:%S"`] Starting linear processes: "
        S=""
        for src in "${SOURCES[@]}";do
            printf "%s%s" "$S" "$src"
            S=", "

            # do the actual call
            gather_${src}
        done
        printf "\n"
    else
        printf "[`date +"%Y-%m-%d %H:%M:%S"`] Starting background processes: "
        S=""
        for src in "${SOURCES[@]}";do
            printf "%s%s" "$S" "$src"
            S=", "
            
            # do the actual call
            gather_${src} >"${OFILE}${src}" 2>&1 &
        done
        printf "\n"
        
        #wait for the processes to actually start. If the system is on a high-load, they wont start this fast
        sleep 2.5
    fi;
    
    
    # the number of existing lockfiles
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
    for src in "${SOURCES[@]}";do
        printf "[`date +"%Y-%m-%d %H:%M:%S"`] Processing: %s\n" "$src"
        
        # do the actual call
        ./process.py -v=1 -module="${src}"
    done
    printf "\n"
elif [ "$PROCESS" == "force" ]; then
    for src in "${SOURCES[@]}";do
        printf "[`date +"%Y-%m-%d %H:%M:%S"`] Processing: %s\n" "$src"
        
        # do the actual call
        ./process.py -v=1 -module="${src}" -forceUpdate=y
        done
        printf "\n"
fi



if [ "$CLEANUP" == "default" ]; then
    printf "[`date +"%Y-%m-%d %H:%M:%S"`] Cleanup\n"
    
    printf "[`date +"%Y-%m-%d %H:%M:%S"`]       Check for empty descriptions & empty statuses\n"
    ./cleanup.py -v=5 -nodescription=1 -fixstatus=1
    
    printf "[`date +"%Y-%m-%d %H:%M:%S"`]       Delete old items\n"
    ./cleanup.py -v=5 -deleteOldItems=1
    
    printf "[`date +"%Y-%m-%d %H:%M:%S"`]       Delete very close duplicates\n"
    ./cleanup.py -v=1 -dup_apply=1 -dup_algorithm_c=desc:0 -dup_algorithm_s=1.7.2 -dup_windowSize=1 -dup_minAutoMatch=0.999
    printf "[`date +"%Y-%m-%d %H:%M:%S"`] Cleanup done\n"
    
elif [ "$CLEANUP" == "thorough" ]; then
    printf "[`date +"%Y-%m-%d %H:%M:%S"`] Cleanup\n"
    #./cleanup.py -v=5 -vacuum=1        <-- this actually deletes items from the DB, dont use it!!!
    
    printf "[`date +"%Y-%m-%d %H:%M:%S"`]       Check for empty descriptions & empty statuses\n"
    ./cleanup.py -v=5 -nodescription=1 -fixstatus=1 
    
    for src in "${SOURCES[@]}";do
        printf "[`date +"%Y-%m-%d %H:%M:%S"`] Cleanup: %s\n" "$src"
        
        # do the actual call
        ./cleanup.py -module="${src}" -vacuum=1
    done
    printf "\n"
    
    printf "[`date +"%Y-%m-%d %H:%M:%S"`]       Delete old items\n"
    ./cleanup.py -v=5 -deleteOldItems=1
    
    printf "[`date +"%Y-%m-%d %H:%M:%S"`]       Delete duplicates\n"
    ./cleanup.py -dup_apply=1 -dup_algorithm_c=desc:0 -dup_algorithm_s=1.7.2 -dup_windowSize=10 -dup_minAutoMatch=0.950
fi
