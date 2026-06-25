#!/bin/sh
set -x

# 20251001
# Ce script télécharge des données sur le datastore
# Il lance un second script python intermédiaire sandwich.py

PYTHONPATH=/opt/conda/env_MF_teledetection 

annee=2025
mois=12
jourj=01

for hh in 17 # 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
do
    for mm in 00 10 20 #30 40 50
    do
        if [ "$mm" = "00" ] ; then minutem=0 ; minutem2=1 ; fi
        if [ "$mm" = "10" ] ; then minutem=1 ; minutem2=2 ; fi
        if [ "$mm" = "20" ] ; then minutem=2 ; minutem2=3 ; fi
        if [ "$mm" = "30" ] ; then minutem=3 ; minutem2=4 ; fi
        if [ "$mm" = "40" ] ; then minutem=4 ; minutem2=5 ; fi
        if [ "$mm" = "50" ] ; then minutem=5 ; minutem2=0 ; fi
            
        repdest=RESULTS
        repsource="/stockage/DATA/${annee}${mois}${jourj}"
        fic="${annee}${mois}${jourj}_${hh}${mm}_mtgi1_satpy_${compo}"

    
        #telechargement des données
        if [ -z "$(ls -A ${repsource}/*OPE*${annee}${mois}${jourj}${hh}${minutem}* 2>/dev/null)" ]
        then
        	echo "Téléchargement des données ${annee}${mois}${jourj}_${hh}${mm}"
            eumdac set-credentials `cat ~/divers/credentials_rc.txt` #identifiant rudy coste

            #665=HR

            eumdac download -c EO:EUM:DAT:0668 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*.nc' --output ${repsource} --threads 10
            #eumdac download -c EO:EUM:DAT:0668 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T05:00:00 --entry '*.nc' --output ${repsource} --threads 10
        



            mv ${repsource}/*/* ${repsource}/
            find ${repsource}/ -type d -empty -delete
        else
            echo "Données ${annee}${mois}${jourj}_${hh}${mm} déjà téléchargées"
        fi          
    
    done
done

