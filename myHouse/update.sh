#!/bin/bash

python ./gather.py -v=5 -sleepp=0.5 -sleepo=0.5 -user-agent="random" -module "anuntul_ro" -category "case-vile" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/"               
python ./gather.py -v=5 -sleepp=0.5 -sleepo=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-2-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/"    
python ./gather.py -v=5 -sleepp=0.5 -sleepo=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-3-cam" -url "http:/www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-1/"     
python ./gather.py -v=5 -sleepp=0.5 -sleepo=0.5 -user-agent="random" -module "anuntul_ro" -category "apt-4-cam" -url "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-1/"    

python ./gather.py -v=5 -sleepp=0 -sleepo=0 -user-agent="real" -module "imobiliare_ro" -category "case-vile" -url "http://www.imobiliare.ro/vanzare-case-vile/bucuresti"


python ./process.py -v=5 -module "anuntul_ro"
python ./process.py -v=5 -module "imobiliare_ro"
