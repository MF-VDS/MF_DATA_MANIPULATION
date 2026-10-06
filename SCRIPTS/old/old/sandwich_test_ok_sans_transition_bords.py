import rasterio
from rasterio.transform import from_bounds
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
import matplotlib.pyplot as plt
from pyresample import AreaDefinition
import matplotlib.colors as mcolors
import xarray as xr
import glob

os.environ['PATH'] = f"/opt/conda/env_MF_teledetection/bin:{os.environ['PATH']}"
os.environ['PATH'] = f"~/.conda/envs/env_MF_teledetection/bin:{os.environ['PATH']}"
os.environ['GDAL_DATA'] = '/opt/conda/env_MF_teledetection/share/gdal'
os.environ['PROJ_LIB'] = '/opt/conda/env_MF_teledetection/share/proj'

yyyy = sys.argv[1]
mm = sys.argv[2]
dd = sys.argv[3]
hh = sys.argv[4]
min_val = sys.argv[5]
minn = sys.argv[6]

input = '/stockage/DATA/' + yyyy + mm + dd + hh + min_val + '0/'

download_dir = os.path.join(os.getcwd(), "../RESULTS")
os.makedirs(download_dir, exist_ok=True)

output = '../RESULTS'

# Charger les données
scn = Scene(filenames=glob.glob(os.path.join(input, '*.nc')), reader='fci_l1c_nc')

# --- Chargement des données ---
scn.load(['vis_06', 'ir_105'])

scn_res = scn.resample(scn['vis_06'].area)
vis = scn_res['vis_06'].values.astype('float32')
ir = scn_res['ir_105'].values.astype('float32')  # ir est déjà en Kelvin

# --- VIS normalisé + gamma ---
vis_min, vis_max = np.nanmin(vis), np.nanmax(vis)
vis_norm = (vis - vis_min) / (vis_max - vis_min)
gamma = 2.0
vis_gamma = np.power(vis_norm, 1/gamma)
# --- RGB du visible ---
vis_rgb = np.dstack([vis_gamma]*3)

# --- NOUVELLE PALETTE KELVIN AVEC INTERPOLATION DOUCE ---
# Définition des valeurs et couleurs de votre palette
kelvin_values = np.array([
    178.15, 183.15, 188.15, 193.15, 198.15, 203.15, 208.15, 213.15, 218.15, 223.15,
    228.15, 233.15, 238.15, 243.15, 248.15, 253.15, 258.15, 263.15, 268.15, 273.15,
    278.15, 283.15, 288.15, 293.15, 298.15, 303.15, 308.15, 313.15
])

colors_kelvin = np.array([
    [170, 140, 255], [210, 110, 255], [255, 190, 250], [180, 140, 150], [80, 30, 10],
    [161, 5, 67], [215, 65, 78], [245, 114, 68], [253, 175, 97], [254, 225, 141],
    [253, 254, 187], [227, 244, 152], [167, 220, 164], [103, 194, 165], [41, 140, 190],
    [90, 83, 165], [90, 83, 165], [190, 190, 190], [175, 175, 175], [160, 160, 160],
    [140, 140, 140], [120, 120, 120], [100, 100, 100], [80, 80, 80], [60, 60, 60],
    [40, 40, 40], [20, 20, 20], [0, 0, 0]
]) / 255.0  # Normalisation 0-1

# Créer une colormap avec interpolation linéaire douce
# On utilise LinearSegmentedColormap qui fait une interpolation automatique
cmap_kelvin = mcolors.LinearSegmentedColormap.from_list(
    'kelvin_palette_smooth',
    list(zip(np.linspace(0, 1, len(kelvin_values)), colors_kelvin)),
    N=256  # Augmenter le nombre de segments pour plus de fluidité
)

# Normalizer pour la palette Kelvin
kelvin_min = kelvin_values.min()
kelvin_max = kelvin_values.max()
norm_kelvin = mcolors.Normalize(vmin=kelvin_min, vmax=kelvin_max)

# --- Application de la palette Kelvin à l'IR ---
ir_kelvin = ir

# Normaliser les valeurs IR selon la plage Kelvin
ir_norm = norm_kelvin(ir_kelvin)
ir_norm = np.clip(ir_norm, 0, 1)  # Éviter les valeurs hors limites

# Appliquer la palette avec interpolation
ir_rgb = cmap_kelvin(ir_norm)[..., :3]

# Gestion des NaN
ir_rgb = np.where(np.isnan(ir_rgb), 0, ir_rgb)

# --- Masque pour les zones froides ---
ir_c = ir - 273.15
mask = ir_c <= -20

# --- Fusion type "sandwich multiplicatif" ---
sandwich = vis_rgb.copy()
sandwich[mask] = vis_rgb[mask] * ir_rgb[mask]

# --- Récupérer zone géographique de la donnée ---
area = scn_res['vis_06'].attrs['area']
crs = area.crs.to_proj4()
extent = area.area_extent
width = area.shape[1]
height = area.shape[0]

# Transformation affine
transform = from_bounds(extent[0], extent[1], extent[2], extent[3], width, height)

# --- Préparer les données en uint8 ---
sandwich_tif = (sandwich * 255).astype(np.uint8)
sandwich_tif = np.transpose(sandwich_tif, (2, 0, 1))

# --- Sauvegarde en GeoTIFF ---
#out_tif = os.path.join(output, "sandwich_kelvin_smooth.tif")
out_tif = os.path.join(output, "sandwich.tif")

with rasterio.open(
    out_tif,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=3,
    dtype=np.uint8,
    crs=crs,
    transform=transform,
) as dst:
    dst.write(sandwich_tif)

print("GeoTIFF avec palette Kelvin lissée sauvegardé :", out_tif) 
