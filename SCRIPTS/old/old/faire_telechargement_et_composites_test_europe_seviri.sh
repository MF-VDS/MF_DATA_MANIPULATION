#!/bin/sh
set -x

# 20251001
# Ce script fabrique des produits composites pour SEVIRI/MSG
# Il lance le script python satpy_composites.py

PYTHONPATH=/opt/conda/env_MF_teledetection 

annee=2026
mois=01
jourj=03
contour=oui

# Définition des domaines
#nomdomaine=france ; latdomaine='46.3' ; londomaine='2.7' ; fenetre="-650000 -650000 650000 650000" ; sizeH='2000' ; sizeL='2000' ;
nomdomaine=europe ; latdomaine='46.5' ; londomaine='10' ; fenetre="-2080000 -1170000 1920000 1080000" ; sizeH='1920' ; sizeL='1080' ;

font='../OUTILS/Police_Marianne/Marianne-Bold.otf'

for hh in 12 #00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 #12 13 14 15 16 17 18 19 20 21 22 23
do
    for mm in 00 #10 # 20 30 40 50
    do
        if [ "$mm" = "00" ] ; then minutem=0 ; minutem2=1 ; fi
        if [ "$mm" = "10" ] ; then minutem=1 ; minutem2=2 ; fi
        if [ "$mm" = "20" ] ; then minutem=2 ; minutem2=3 ; fi
        if [ "$mm" = "30" ] ; then minutem=3 ; minutem2=4 ; fi
        if [ "$mm" = "40" ] ; then minutem=4 ; minutem2=5 ; fi
        if [ "$mm" = "50" ] ; then minutem=5 ; minutem2=0 ; fi
            
        repdest=RESULTS
        repsource="/stockage/DATA/SEVIRI/${annee}${mois}${jourj}"
        fic="${annee}${mois}${jourj}_${hh}${mm}_msg_satpy_${compo}"
    
        # Création répertoire source si besoin
        if [ ! -d "${repsource}" ]
        then
            mkdir -p ${repsource}
        fi
    
        # Téléchargement des données SEVIRI/MSG
        # Note: Les collections EUMETSAT pour SEVIRI/MSG sont différentes
        # EO:EUM:DAT:MSG:HRSEVIRI pour HRIT
        # EO:EUM:DAT:MSG:0deg pour données natales
        if [ -z "$(ls -A ${repsource}/*H-000-MSG*${annee}${mois}${jourj}${hh}${minutem}* 2>/dev/null)" ]
        then
            echo "Téléchargement des données SEVIRI ${annee}${mois}${jourj}_${hh}${mm}"
            eumdac set-credentials ogQ9Mpf0f1GsPIyfg0w4md2ZJdsa b9uXQcvk7cmEMmRJ2S2kU90qq8oa #
        
            # Téléchargement des canaux principaux SEVIRI (format HRIT)
            # Les canaux MSG: VIS006, VIS008, IR_016, IR_039, WV_062, WV_073, IR_087, IR_097, IR_108, IR_120, IR_134
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*VIS006*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*VIS008*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*IR_016*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*IR_039*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*WV_062*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*WV_073*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*IR_087*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*IR_097*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*IR_108*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*IR_120*' \
                --output ${repsource} \
                --threads 10
                
            eumdac download -c EO:EUM:DAT:MSG:HRSEVIRI \
                --start ${annee}-${mois}-${jourj}T${hh}:${minutem}0:00 \
                --end ${annee}-${mois}-${jourj}T${hh}:${minutem2}5:00 \
                --entry '*IR_134*' \
                --output ${repsource} \
                --threads 10
            
            # Déplacement des fichiers téléchargés
            mv ${repsource}/*/* ${repsource}/ 2>/dev/null
            find ${repsource}/ -type d -empty -delete
        else
            echo "Données SEVIRI ${annee}${mois}${jourj}_${hh}${mm} déjà téléchargées"
        fi    
    
        echo "Création de ${fic}... "

        # Liste des composites disponibles pour SEVIRI
        for compo in convection #dust night_fog sandwich cloudtop day_microphysics 
        do

            nomcompo=${compo}
            if [ "$compo" = "natural_color" ] ; then nomcompo="Natural Color RGB" ; fi
            if [ "$compo" = "ash" ] ; then nomcompo="Ash RGB" ; fi
            if [ "$compo" = "airmass" ] ; then nomcompo="Airmass RGB" ; fi
            if [ "$compo" = "convection" ] ; then nomcompo="Convection RGB" ; fi
            if [ "$compo" = "dust" ] ; then nomcompo="Dust RGB" ; fi
            if [ "$compo" = "night_fog" ] ; then nomcompo="Night Fog RGB" ; fi
            if [ "$compo" = "sandwich" ] ; then nomcompo="Sandwich" ; fi
            if [ "$compo" = "cloudtop" ] ; then nomcompo="Cloud Top RGB" ; fi
            if [ "$compo" = "day_microphysics" ] ; then nomcompo="Day Microphysics RGB" ; fi

            repdest=../RESULTS
            fic=${annee}${mois}${jourj}_${hh}${mm}_msg_satpy_${compo}

            if [ -f ${repdest}/${fic}_france_1x1.jpg ]
            then
                rm ${repdest}/${fic}*
            fi 

            # Création répertoire composites si besoin
            if [ ! -d "composites/$compo" ]
            then
                mkdir -p composites/$compo
            fi

            if [ ! -d "${repdest}" ]
            then
                mkdir -p ${repdest}
            fi
            
            echo minute= $minutem

            # Appel du script Python
            python satpy_composites_seviri.py $compo ${annee} ${mois} ${jourj} ${hh} ${minutem} 3000 
        
            echo -n "$fic : decoupe tif et creation jpg"
            mv ${repdest}/${compo}_${annee}${mois}${jourj}_${hh}${mm}_satpy.tif ${repdest}/${fic}.tif 2>/dev/null

            echo "$fic domaine ${nomdomaine}"
            # Reprojection orthographique
            gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te ${fenetre} -r cubic ${repdest}/${fic}.tif ${repdest}/${fic}_${nomdomaine}_vraie_taille.tif &
            gdalwarp -q -overwrite -t_srs "+proj=ortho lat_0=${latdomaine} lon_0=${londomaine}" -te ${fenetre} -ts ${sizeH} ${sizeL} -r cubic ${repdest}/${fic}.tif ${repdest}/${fic}_${nomdomaine}.tif &
            wait
            
            # Conversion en JPEG
            convert ${repdest}/${fic}_${nomdomaine}_vraie_taille.tif ${repdest}/${fic}_${nomdomaine}_vraie_taille.jpg
            convert -resize ${sizeH}x${sizeL} ${repdest}/${fic}_${nomdomaine}_vraie_taille.tif ${repdest}/${fic}_${nomdomaine}.jpg
            wait
            
            # Ajout de contour
            if [ "$contour" = "oui" ]
            then
                echo "creation contour"
                gdal_rasterize -q -b 1 -burn 255 -b 2 -burn 255 -b 3 -burn 255 -l world-administrative-boundaries ../OUTILS/boundary/world-administrative-boundaries.shp ${repdest}/${fic}_${nomdomaine}.tif > /dev/null 2>&1
            fi                            
            
            # Conversion finale
            convert ${repdest}/${fic}_${nomdomaine}.tif ${repdest}/${fic}_${nomdomaine}.jpg
            
            # Ajout de texte avec informations
            heure=$hh
            min=$mm
            convert ${repdest}/${fic}_${nomdomaine}.jpg -font ${font} -pointsize 30 -fill '#ffffff' -annotate +15+36 "MSG/SEVIRI | $nomcompo - ${jourj}/${mois}/${annee} à ${heure}:${min} UTC" ${repdest}/${fic}_${nomdomaine}_final.jpg
            
            # Nettoyage
            mv ${repdest}/${fic}_${nomdomaine}_final.jpg ${repdest}/${fic}_${nomdomaine}.jpg
            rm ${repdest}/*.xml ${repdest}/*_vraie_taille.* 2>/dev/null
        done
    done
done