#!/bin/sh
set -x

# 20251001
# Ce script fabrique un produit Sandwich
# Il lance un second script python intermédiaire sandwich.py

PYTHONPATH=/opt/conda/env_MF_teledetection 

annee=2026
mois=05
jourj=27
contour=oui

#nomdomaine=france ; latdomaine='46.3' ; londomaine='2.7' ;  fenetre="-650000 -650000 650000 650000" ; sizeH='2000' ; sizeL='2000' ;
#nomdomaine=france ; latdomaine='46.5' ; londomaine='1' ;  fenetre="-1120000 -630000 1120000 630000" ; sizeH='1920' ; sizeL='1080' ;
nomdomaine=europe ; latdomaine='46.5' ; londomaine='1' ;  fenetre="-2080000 -1170000 1920000 1080000" ; sizeH='1920' ; sizeL='1080' ;

#rm ~/MF_DATA_MANIPULATION/RESULTS/* 2>/dev/null
font='../OUTILS/Police_Marianne/Marianne-Bold.otf'

for hh in 16  #00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 #12 13 14 15 16 17 18 19 20 21 22 23
do
    for mm in 30 #10 # 20 30 40 50
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
    
        #creation repertoire RES si besoin
        if [ ! -d "${repsource}" ]
        	then
        	mkdir ${repsource}
        fi
    
        #telechargement des données
        if [ -z "$(ls -A ${repsource}/*OPE*${annee}${mois}${jourj}${hh}${minutem}* 2>/dev/null)" ]
        then
        	echo "Téléchargement des données ${annee}${mois}${jourj}_${hh}${mm}"
            eumdac set-credentials `cat ~/divers/credentials_rc.txt` #identifiant rudy coste

            #665=HR
        
            eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0033.nc' --output ${repsource} --threads 10
            eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0034.nc' --output ${repsource} --threads 10
            eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0035.nc' --output ${repsource} --threads 10 #france
            eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0036.nc' --output ${repsource} --threads 10 #france
            eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0037.nc' --output ${repsource} --threads 10 #france
            eumdac download -c EO:EUM:DAT:0665 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0038.nc' --output ${repsource} --threads 10
    
            eumdac download -c EO:EUM:DAT:0662 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0033.nc' --output ${repsource} --threads 10
            eumdac download -c EO:EUM:DAT:0662 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0034.nc' --output ${repsource} --threads 10
            eumdac download -c EO:EUM:DAT:0662 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0035.nc' --output ${repsource} --threads 10 #france
            eumdac download -c EO:EUM:DAT:0662 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0036.nc' --output ${repsource} --threads 10 #france
            eumdac download -c EO:EUM:DAT:0662 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0037.nc' --output ${repsource} --threads 10 #france
            eumdac download -c EO:EUM:DAT:0662 --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}0:00 --entry '*0038.nc' --output ${repsource} --threads 10
            mv ${repsource}/*/* ${repsource}/
            find ${repsource}/ -type d -empty -delete
        else
            echo "Données ${annee}${mois}${jourj}_${hh}${mm} déjà téléchargées"
        fi    
    
        echo "Création de ${fic}...  "

        
        for compo in true_color  #cimss_cloud_type true_color cloud_phase cloud_type day_microphysics ash airmass fire_temperature cloud_phase cloudtop convection day_severe_storms dust
        do

            nomcompo=${compo}
            if [ "$compo" = "cloud_phase" ] ;  then nomcompo="Cloud Phase RGB" ; fi
            if [ "$compo" = "cimss_cloud_type" ] ;  then nomcompo="Cloud Type RGB" ; fi
            if [ "$compo" = "truecolor" ] ;  then nomcompo="Geocolor RGB" ; fi
            if [ "$compo" = "convection" ] ;  then nomcompo="Convection RGB" ; fi
            if [ "$compo" = "day_microphysics" ] ;  then nomcompo="Day Microphysics RGB" ; fi
            if [ "$compo" = "colnat" ] ;  then nomcompo="Natural Color RGB" ; fi
            if [ "$compo" = "ash" ] ;  then nomcompo="Ash RGB" ; fi
            if [ "$compo" = "sandwich" ] ;  then nomcompo="Sandwich" ; fi
            if [ "$compo" = "airmass" ] ;  then nomcompo="Airmass RGB" ; fi
            if [ "$compo" = "nMiPhy" ] ;  then nomcompo="Fog / Low clouds RGB" ; fi
            if [ "$compo" = "fire_temperature" ] ;  then nomcompo="Fire temperature RGB" ; fi
            if [ "$compo" = "day_severe_storm" ] ;  then nomcompo="Day Severe Storm RGB" ; fi

            repdest=../RESULTS
            fic=${annee}${mois}${jourj}_${hh}${mm}_mtgi1_satpy_${compo}

            if [ -f ${repdest}/${fic}_france_1x1.jpg ]
            then
                rm ${repdest}/${fic}*
            fi	

            #creation repertoire RES si besoin
            if [ ! -d "composites/$compo" ]
                then
                mkdir composites/$compo
            fi

            if [ ! -d "${repdest}" ]
                then
                mkdir ${repdest}
            fi
            echo minute= $minutem

            python  satpy_composites.py $compo ${annee} ${mois} ${jourj} ${hh} ${minutem} 2000 
        
            echo -n "$fic : decoupe tif et creation jpg"
            mv ${repdest}/${compo}_${annee}${mois}${jourj}_${hh}${mm}_satpy.tif ${repdest}/${fic}.tif

            echo "$fic domaine ${nomdomaine}"
            gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te ${fenetre} -r cubic ${repdest}/${fic}.tif ${repdest}/${fic}_${nomdomaine}_vraie_taille.tif &
            gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te ${fenetre} -ts ${sizeH} ${sizeL} -r cubic ${repdest}/${fic}.tif ${repdest}/${fic}_${nomdomaine}.tif &
            wait
            convert ${repdest}/${fic}_${nomdomaine}_vraie_taille.tif ${repdest}/${fic}_${nomdomaine}_vraie_taille.jpg
            convert -resize ${sizeH}x${sizeL} ${repdest}/${fic}_${nomdomaine}_vraie_taille.tif ${repdest}/${fic}_${nomdomaine}.jpg
            wait
            #ajout contour trait de cote
            if [ "$contour" = "oui" ]
            then
                    echo "creation contour"
                    gdal_rasterize -q -b 1 -burn 255 -b 2 -burn 255 -b 3 -burn 255 -l world-administrative-boundaries ../OUTILS/boundary/world-administrative-boundaries.shp ${repdest}/${fic}_${nomdomaine}.tif > /dev/null 2>1  # frontière blanche
            fi                            
            composite -quiet -geometry +1600+1936 ../OUTILS/logo_MF-400.png ${repdest}/${fic}_${nomdomaine}.tif ${repdest}/${fic}_${nomdomaine}.tif
            composite -quiet -geometry +0+0 ../OUTILS/bandeau_bleu_2000x2000.png ${repdest}/${fic}_${nomdomaine}.tif ${repdest}/${fic}_${nomdomaine}.jpg
            convert  ${repdest}/${fic}_${nomdomaine}_contour.jpg -font ${font}  -pointsize 30 -fill '#ffffff' -annotate +15+36  "Meteosat-12 | $nomcompo - ${jourj}/${mois}/${annee} à ${heure}:${min} UTC" ${repdest}/${fic}_${nomdomaine}.jpg            
            
            rm  ${repdest}/*.xml  # ${repdest}/*.tif >/dev/null
        

        done
    done
done

