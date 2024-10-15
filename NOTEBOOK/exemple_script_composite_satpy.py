#!/usr/bin/env python
# coding: utf-8

#exemple de script python pour réaliser une composite satpy
#plus d'info dans jupyter note book MTG_satpy_chunk.ipynb
# lancement du script : exemple : python exemple_script_composite_satpy.py cloud_phase


from satpy.scene import Scene
from satpy import find_files_and_readers
from datetime import datetime
import sys
from pyresample.geometry import AreaDefinition
import numpy as np
import os
from osgeo import gdal
from PIL import Image
import subprocess
from IPython.display import display,HTML
import glob
os.environ['PATH'] = f"~/.conda/envs/env_MF_stage/bin:{os.environ['PATH']}" 
os.environ['GDAL_DATA'] = '/home/coster/.conda/envs/env_MF_stage/share/gdal'
os.environ['PROJ_LIB'] = '/home/coster/.conda/envs/env_MF_stage/share/proj'

shell=True

input = '/stockage/DATA/chunks_mtg_20240923/'

download_dir = os.path.join(os.getcwd(), "../RESULTS")
os.makedirs(download_dir, exist_ok=True)

output = '../RESULTS'

composite_name =sys.argv[1]

annee='2024'
mois='09'
jour='23'
heure='14'

print('Traitement de ' + composite_name + ' en cours, le ' + jour + '/' + mois + '/' + annee + ' à '+ heure + '00UTC' )

yyyy=int(annee)
mm=int(mois)
dd=int(jour)
hh_debut=int(heure)
min_debut=int('00')
hh_fin=int(heure)
min_fin=int('10')

reader_to_use = "fci_l1c_nc"

filename = (output + '/RGB_' + composite_name )

myfiles = find_files_and_readers(base_dir=input,
                                 start_time=datetime(yyyy,mm,dd,hh_debut,min_debut),
                                 end_time=datetime(yyyy,mm,dd,hh_fin,min_fin),
                                 reader=reader_to_use)

scn = Scene(filenames=myfiles)
scn.load([composite_name], upper_right_corner='NE')
natscn = scn.resample(scn.coarsest_area(), resampler='nearest')

print(' --- Création du tif')

natscn.save_dataset(composite_name, filename=filename + '.tif')

print(' --- Redimmensionnement et découpe')

cmd1 = ['gdalwarp', '-overwrite', '-ts', '1000', '1000', filename + '.tif', filename + '_globe.jpg' ]
subprocess.run(cmd1)

cmd2 = [ 'gdalwarp', '-overwrite',  '-t_srs', "EPSG:4326", '-te', '2', '5', '18', '16',  filename + '.tif', filename + '_decoupe.tif' ]
subprocess.run(cmd2)

cmd3 = [ 'gdal_rasterize', '-q', '-b', '1', '-burn', '255', '-b', '2', '-burn', '255', '-b', '3', '-burn', '255', '-l', 'world-administrative-boundaries', '../OUTILS/boundary/world-administrative-boundaries.shp', filename + '_decoupe.tif' ]
subprocess.run(cmd3)

cmd4 = [ 'convert', '-resize', '1200', filename + '_decoupe.tif', filename + '_decoupe.jpg']
subprocess.run(cmd4)

cmdrm = [ 'rm', '-f', filename + '.tif',  filename + '_decoupe.tif', filename + '_globe.jpg.aux.xml' ]
subprocess.run(cmdrm)



