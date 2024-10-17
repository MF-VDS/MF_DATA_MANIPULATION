#!/bin/sh
#set -x

#source  ~/anaconda3/etc/profile.d/conda.sh
conda activate env_MF_stage
PYTHONPATH=/home/vds/anaconda3/envs/satpy_test2/bin # A modifier !!!

#dj=`date +%Y%m%d`
#hh=$(date +%H)
dj='20240903'
d=$(date +%d)
hh=$(date +%H)

annee=2024
mois=08
jourj=15
choix=facon
nomdomaine=etna
latdomaine='37.5'
londomaine='15'

for hh in 00 #01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 #12 13 14 15 16 17 18 19 20 21 22 23
do
    for mm in 00 #10 20 30 40 50
    do
    
    if [ "$mm" = "00" ] ; then minutem=0 ; fi
    if [ "$mm" = "10" ] ; then minutem=1 ; fi
    if [ "$mm" = "20" ] ; then minutem=2 ; fi
    if [ "$mm" = "30" ] ; then minutem=3 ; fi
    if [ "$mm" = "40" ] ; then minutem=4 ; fi
    if [ "$mm" = "50" ] ; then minutem=5 ; fi

        for compo in ash # geo_color cloud_phase cloud_type day_microphysics ash airmass fire_temperature cloud_phase cloudtop convection
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

            repdest=composites/${compo}/${annee}${mois}${jourj}
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

            python  creer_img_fci_satpy_chunk.py $compo ${annee} ${mois} ${jourj} ${hh} ${minutem} 2000 
        
            echo -n "$fic : "

            echo "decoupe tif et creation jpg"
            mv ${compo}_${annee}${mois}${jourj}_${hh}${mm}_satpy.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}.tif

            echo "$fic domaine ${nomdomaine}"
            #gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te -500000 -500000 500000 500000 -r cubic  ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.tif # domaine 
            #gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te -840000 -472500 840000 472500 -r cubic  ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.tif # domaine
            gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te -600000 -337500 600000 337500 -r cubic  ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.tif
            if [ ! -e ${repdest}/${compo}_${nomdomaine}_contour.png ]
            then
                echo "contour------------"
                ./creer_image_transparente_aveccontour.sh ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.tif ${repdest}/${compo}_${nomdomaine}_contour.tif /data/meta/shapefiles/10m_coastline.shp
                convert -quiet ${repdest}/${compo}_${nomdomaine}_contour.tif ${repdest}/${compo}_${nomdomaine}_contour.png
            fi
            convert -quiet ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.tif ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_0.png
            composite -quiet -geometry +0+0 ${repdest}/${compo}_${nomdomaine}_contour.png ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_0.png ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1.jpg # ajout contour
            #convert -quiet ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1.jpg -font Liberation-Sans-Bold -pointsize 30 -fill '#ffffff'  -annotate +40+50 "MTG $nomcompo / ${annee}${mois}${jourj} - ${hh}${mm}UTC" ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.jpg
            convert -quiet ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1.jpg -font Liberation-Sans-Bold -pointsize 11 -fill '#ffffff'  -annotate +12+12 "MTG $nomcompo / ${annee}${mois}${jourj} - ${hh}${mm}UTC" ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.jpg #ajout dateheure
            convert -resize 1920x1080 ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}.jpg ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1920-1080.png

            rm -f  ${repdest}/${annee}${mois}${jourj}_${hh}${mm}_satpy_${compo}_${nomdomaine}_1.jpg  #${repdest}/*.tif
            rm -f  ${repdest}/*med_0.* ${repdest}/*_med_1.* 
            rm  ${repdest}/${fic}_*hd*.jpg ${repdest}/${fic}*1800x1800*.png   ${repdest}/${fic}_*large.tif #${repdest}/${fic}_*europe.tif
            rm  ${repdest}/*_.jpg ${repdest}/*.xml #${repdest}/${annee}${mois}${jourj}_${hh}00_satpy_${compo}.tif

        done
    done
done

conda deactivate
