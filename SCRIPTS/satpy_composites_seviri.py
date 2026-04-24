#!/usr/bin/env python3
"""
satpy_composites.py - Script pour créer des composites SEVIRI/MSG avec SatPy
"""

import os
import sys
import glob
import logging
from datetime import datetime

import hdf5plugin
from satpy import Scene
from pyresample import create_area_def

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) != 8:
        print("Usage: python satpy_composites.py <composite> <yyyy> <mm> <dd> <hh> <min> <resolution>")
        print("Example: python satpy_composites.py natural_color 2025 08 13 12 00 3000")
        sys.exit(1)
   
    # Récupération des arguments
    compo = sys.argv[1]
    yyyy = sys.argv[2]
    mm = sys.argv[3]
    dd = sys.argv[4]
    hh = sys.argv[5]
    min = sys.argv[6]
    varres = sys.argv[7]
    resol = int(varres)
   
    # Construction du chemin des données SEVIRI
    # Format des fichiers: H-000-MSG4__-MSG4________-IR_108___-000001___-202508131200-C_
    base_path = '/stockage/DATA/SEVIRI'
    date_str = f"{yyyy}{mm}{dd}"
    time_str = f"{hh}{min}"
   
    # Plusieurs patterns possibles pour les fichiers SEVIRI
    path_to_data = os.path.join(base_path, date_str)
   
    # Patterns de fichiers SEVIRI
    patterns = [
        os.path.join(path_to_data, f"*{date_str}{time_str}*.h5"),  # Format HDF5
        os.path.join(path_to_data, f"*{date_str}{time_str}*.nc"),  # Format NetCDF
        os.path.join(path_to_data, f"*{date_str}{time_str}*.nat"), # Format natif
        os.path.join(path_to_data, f"H-000-MSG*{date_str}{time_str}*"),  # Format HRIT
    ]
   
    # Recherche des fichiers
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
   
    if not files:
        logger.error(f"Aucun fichier SEVIRI trouvé dans {path_to_data} pour {date_str}{time_str}")
        logger.error(f"Patterns recherchés: {patterns}")
        sys.exit(1)
   
    logger.info(f"Nombre de fichiers SEVIRI trouvés: {len(files)}")
    logger.info(f"Premier fichier: {files[0]}")
   
    # Détermination du reader en fonction du format de fichier
    if any(f.endswith('.h5') for f in files[:5]):
        reader = 'seviri_l1b_hrit'
    elif any(f.endswith('.nat') for f in files[:5]):
        reader = 'seviri_l1b_native'
    else:
        reader = 'seviri_l1b_nc'  # Par défaut pour NetCDF
   
    logger.info(f"Utilisation du reader: {reader}")
   
    try:
        # Initialisation de la scène SEVIRI
        logger.info(f"Initialisation de la scène SEVIRI avec {len(files)} fichiers")
        scn = Scene(filenames=files, reader=reader)
       
        # Liste des composites disponibles pour SEVIRI
        available_composites = {
            'natural_color': ['natural_color'],
            'ash': ['ash'],
            'airmass': ['airmass'],
            'convection': ['convection'],
            'dust': ['dust'],
            'night_fog': ['night_fog'],
            'day_microphysics': ['day_microphysics'],
            'cloudtop': ['cloudtop'],
            'true_color': ['true_color'],
            'hrv_fog': ['hrv_fog'],
            'snow': ['snow'],
            'ndvi': ['ndvi'],
        }
       
        if compo not in available_composites:
            logger.warning(f"Composite {compo} non reconnu. Tentative de chargement quand même...")
            composite_list = [compo]
        else:
            composite_list = available_composites[compo]
       
        # Chargement du composite
        logger.info(f"Chargement du composite: {compo}")
       
        try:
            # Première tentative avec la résolution spécifiée
            scn.load(composite_list, resolution=resol)
        except Exception as e:
            logger.warning(f"Chargement avec résolution {resol} échoué: {e}")
            logger.info("Tentative de chargement avec résolution native...")
           
            # Tentative sans spécifier la résolution
            scn.load(composite_list)
       
        # Resample si nécessaire
        if scn[compo].area is not None:
            logger.info(f"Rééchantillonnage à {resol}m...")
           
            # Création d'une area definition pour l'Europe
            target_area = create_area_def(
                'europe_lambert',
                {'proj': 'lcc', 'lat_0': 50, 'lon_0': 10, 'lat_1': 35, 'lat_2': 65,
                 'x_0': 0, 'y_0': 0, 'ellps': 'WGS84', 'units': 'm'},
                area_extent=[-2500000, -2000000, 2500000, 2000000],  # Europe
                resolution=(resol, resol),
                description='Europe Lambert Conformal'
            )
           
            # Resample
            resampled_scn = scn.resample(target_area, resampler='native')
        else:
            resampled_scn = scn
       
        # Sauvegarde du résultat
        output_dir = '../RESULTS'
        os.makedirs(output_dir, exist_ok=True)
       
        output_filename = os.path.join(
            output_dir,
            f"{compo}_{yyyy}{mm}{dd}_{hh}{min}_satpy.tif"
        )
       
        logger.info(f"Sauvegarde du dataset dans: {output_filename}")
       
        # Options de sauvegarde GeoTIFF
        save_kwargs = {
            'filename': output_filename,
            'tiled': True,
            'compress': 'lzw',
            'driver': 'GTiff',
            'dtype': 'uint8',
            'enhance': False,
        }
       
        # Vérification si le dataset existe
        if compo in resampled_scn:
            resampled_scn.save_dataset(compo, **save_kwargs)
            logger.info(f"Composite {compo} sauvegardé avec succès")
           
            # Affichage d'informations sur l'image générée
            dataset = resampled_scn[compo]
            logger.info(f"Dimensions: {dataset.shape}")
            logger.info(f"Type de données: {dataset.dtype}")
            logger.info(f"Valeurs min/max: {dataset.values.min():.2f}/{dataset.values.max():.2f}")
           
        elif 'true_color' in resampled_scn and compo == 'natural_color':
            # Fallback: true_color est souvent disponible
            logger.info(f"Composite {compo} non trouvé, utilisation de 'true_color'")
            resampled_scn.save_dataset('true_color', **save_kwargs)
        else:
            logger.error(f"Composite {compo} non disponible dans la scène")
            logger.info(f"Composites disponibles: {list(resampled_scn.keys())}")
            sys.exit(1)
           
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
   
    logger.info("Traitement terminé avec succès")

if __name__ == "__main__":
    main() 