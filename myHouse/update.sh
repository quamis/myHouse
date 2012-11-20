#!/bin/bash

python ./gather.py -v=1 -sleepp 2 -sleepo 1 -user-agent="random" -module "anuntul_ro" -category "case-vile" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/"               
python ./gather.py -v=1 -sleepp 2 -sleepo 1 -user-agent="random" -module "anuntul_ro" -category "apt-2-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/"    
python ./gather.py -v=1 -sleepp 2 -sleepo 1 -user-agent="random" -module "anuntul_ro" -category "apt-3-cam" -url "http:/www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-1/"     
python ./gather.py -v=1 -sleepp 2 -sleepo 1 -user-agent="random" -module "anuntul_ro" -category "apt-4-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-1/"    


python ./process.py -v=1 -module "anuntul_ro"
