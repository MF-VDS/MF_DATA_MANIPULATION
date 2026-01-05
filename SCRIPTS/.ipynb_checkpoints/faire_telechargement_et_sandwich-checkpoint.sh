#!/bin/sh
#set -x

# 20251001
# Ce script fabrique un produit Sandwich
# Il lance un second script python intermédiaire sandwich.py

PYTHONPATH=/opt/conda/env_MF_teledetection 

annee=2025
mois=06
jourj=25
#Definir zone centre de la zone à découper
latdomaine='46'
londomaine='2'
contour=oui
domaine_decoupe='-640000 -360000 640000 360000' # projection ortho
#domaine_decoupe='-640000 -360000 640000 360000' #petit domaine
#domaine_decoupe='-800000 -450000 800000 450000' #petit domaine 
#domaine_decoupe='-1600000 -900000 1600000 900000' #grand domaine
#domaine_decoupe='-3200000 -1800000 3200000 1800000' #très grand domaine

rm ~/MF_DATA_MANIPULATION/RESULTS/* 2>/dev/null


for hh in 18 #00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 #12 13 14 15 16 17 18 19 20 21 22 23
do
    for mm in 20 #10 20 30 40 50
    do
    if [ "$mm" = "00" ] ; then minutem=0 ; minutem2=1 ; fi
    if [ "$mm" = "10" ] ; then minutem=1 ; minutem2=2 ; fi
    if [ "$mm" = "20" ] ; then minutem=2 ; minutem2=3 ; fi
    if [ "$mm" = "30" ] ; then minutem=3 ; minutem2=4 ; fi
    if [ "$mm" = "40" ] ; then minutem=4 ; minutem2=5 ; fi
    if [ "$mm" = "50" ] ; then minutem=5 ; minutem2=0 ; fi
        
    repdest=RESULTS
    repsource="/stockage/DATA/${annee}${mois}${jourj}"
    fic=${annee}${mois}${jourj}_${hh}${mm}_mtgi1_satpy_sandwich

    #creation repertoire RES si besoin
    if [ ! -d "${repsource}" ]
    	then
    	mkdir ${repsource}
    fi

    #telechargement des données
    if [ -z "$(ls -A "${repsource}" 2>/dev/null)" ]
    then
    	echo "Téléchargement des données ${annee}${mois}${jourj}_${hh}${mm}"
        eumdac set-credentials ogQ9Mpf0f1GsPIyfg0w4md2ZJdsa b9uXQcvk7cmEMmRJ2S2kU90qq8oa #identifiant rudy coste
        eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0033.nc' --output ${repsource} --threads 5
        eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0034.nc' --output ${repsource} --threads 5
        eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0035.nc' --output ${repsource} --threads 5
        eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0036.nc' --output ${repsource} --threads 5
        eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0037.nc' --output ${repsource} --threads 5
        mv ${repsource}/*/* ${repsource}/
        find ${repsource}/ -type d -empty -delete
    else
        echo "Données ${annee}${mois}${jourj}_${hh}${mm} déjà téléchargées"
    fi    

    

    echo "Création de ${fic}...  "

    #lancement script python satpy
    # date à modifier dans ce script également si besoin
    #python  sandwich_test_3D.py ${annee} ${mois} ${jourj} ${hh} ${minutem} ${minutem2} #> /dev/null 2>1
    #python sandwich_test.py ${annee} ${mois} ${jourj} ${hh} ${minutem} ${minutem2} 0.1 #> /dev/null 2>1  
    python sandwich_test.py ${annee} ${mois} ${jourj} ${hh} ${minutem} ${minutem2} 0.1 #> /dev/null 2>1  
        
    

    echo "decoupe tif et creation jpg"
    mv ../RESULTS/sandwich.tif ../RESULTS/${fic}.tif
    convert -resize 2000 ../RESULTS/${fic}.tif ../RESULTS/${fic}.jpg > /dev/null 2>1
    convert ../RESULTS/${fic}.tif ../RESULTS/${fic}_HD.jpg > /dev/null 2>1

    #decoupe du domaine
    gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te ${domaine_decoupe} -r cubic  ../RESULTS/${fic}.tif ../RESULTS/${fic}_decoupe.tif > /dev/null 2>1
    #ajout contour trait de cote
    if [ "$contour" = "oui" ]
    then
        gdal_rasterize -q -b 1 -burn 255 -b 2 -burn 255 -b 3 -burn 255 -l world-administrative-boundaries ../OUTILS/boundary/world-administrative-boundaries.shp ../RESULTS/${fic}_decoupe.tif > /dev/null 2>1  # frontière blanche
    fi

    #augmentation gamma si besoin
    #gdal_translate -scale -exponent 0.6 ../RESULTS/${fic}_decoupe.tif ../RESULTS/${fic}_gamma_decoupe.tif

    #Création jpg et redimmensionnement
    convert -resize 1920x1080 ../RESULTS/${fic}_decoupe.tif ../RESULTS/${fic}_decoupe.jpg > /dev/null 2>1
    convert ../RESULTS/${fic}_decoupe.tif ../RESULTS/${fic}_decoupe_HD.jpg > /dev/null 2>1
    #convert -resize 1920x1080 ../RESULTS/${fic}_gamma_decoupe.tif ../RESULTS/${fic}_gamma_decoupe.jpg > /dev/null 2>1

    #rm -f ../RESULTS/${fic}.tif



    done
done

