#!/bin/sh
#set -x

#source  ~/anaconda3/etc/profile.d/conda.sh
#conda activate env_MF_stage
PYTHONPATH=/opt/conda/env_MF_teledetection # A modifier !!!

#dj=`date +%Y%m%d`
#hh=$(date +%H)
#dj='20240903'
#d=$(date +%d)
#hh=$(date +%H)

annee=2025
mois=11
jourj=12
choix=facon
nomdomaine=France ; latdomaine='45' ; londomaine='0'

for hh in 12 #00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 #12 13 14 15 16 17 18 19 20 21 22 23
do
    for mm in 00 #10 20 30 40 50
    do
    
    if [ "$mm" = "00" ] ; then minutem=0 ; fi
    if [ "$mm" = "10" ] ; then minutem=1 ; fi
    if [ "$mm" = "20" ] ; then minutem=2 ; fi
    if [ "$mm" = "30" ] ; then minutem=3 ; fi
    if [ "$mm" = "40" ] ; then minutem=4 ; fi
    if [ "$mm" = "50" ] ; then minutem=5 ; fi

        for compo in dust #true_color cloud_phase cloud_type day_microphysics ash airmass fire_temperature cloud_phase cloudtop convection dust
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

            repdest=../RESULTS
            fic=${compo}_${annee}${mois}${jourj}_${hh}${mm}_mtgi1_satpy

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
        
            echo -n "$fic : "

            echo "decoupe tif et creation jpg"
            mv ${repdest}/${compo}_${annee}${mois}${jourj}_${hh}${mm}_satpy.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}.tif

            echo "$fic domaine ${nomdomaine}"
            gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te -3200000 -1800000 3200000 1800000 -r cubic  ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.tif

            convert -quiet ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1.jpg
            convert -quiet ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1.jpg -font Liberation-Sans-Bold -pointsize 11 -fill '#ffffff'  -annotate +12+12 "MTG $nomcompo / ${annee}${mois}${jourj} - ${hh}${mm}UTC" ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.jpg #ajout dateheure
            convert -resize 1920x1080 ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.jpg ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1920-1080.png
            convert -quiet -resize 2000 ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}.jpg

            rm -f  ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1.jpg  #${repdest}/*.tif
            rm -f  ${repdest}/*med_0.* ${repdest}/*_med_1.* 
            rm  ${repdest}/${fic}_*hd*.jpg ${repdest}/${fic}*1800x1800*.png   ${repdest}/${fic}_*large.tif #${repdest}/${fic}_*europe.tif
            rm  ${repdest}/*_.jpg ${repdest}/*.xml #${repdest}/${annee}${mois}${jourj}_${hh}00_satpy_${compo}.tif
            rm  ${repdest}/*.tif

        done
    done
done

conda deactivate
