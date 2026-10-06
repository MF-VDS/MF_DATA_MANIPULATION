#!/usr/bin/env python3

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
from PIL import Image, ImageFilter
import subprocess
from IPython.display import display,HTML
import matplotlib.pyplot as plt
from pyresample import create_area_def
import matplotlib.colors as mcolors
import xarray as xr
import glob
import warnings
warnings.filterwarnings("ignore",category=RuntimeWarning)
warnings.filterwarnings("ignore",category=UserWarning)

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

# ZONE D'INTERET OPTIMISEE : 5W 10E 35S 50N
TARGET_BOUNDS = (-6, 42, 8, 51)  # left, bottom, right, top

input = '/stockage/DATA/' + yyyy + mm + dd + '/'

download_dir = os.path.join(os.getcwd(), "../RESULTS")
os.makedirs(download_dir, exist_ok=True)

output = '../RESULTS'

# Charger les données
pattern = f"*{yyyy}{mm}{dd}{hh}{min_val}*.nc"
scn = Scene(filenames=glob.glob(os.path.join(input, pattern)), reader='fci_l1c_nc')

# --- Chargement des données ---
scn.load(['vis_06', 'ir_105'])

print("=== APPROCHE OPTIMISÉE ===")
print("Création d'une zone cible personnalisée...")

# Obtenir l'area originale
original_area = scn['vis_06'].attrs['area']

# Méthode SIMPLE : Créer une area definition basique pour notre zone
# Calculer une résolution approximative (en degrés)
width_deg = TARGET_BOUNDS[2] - TARGET_BOUNDS[0]  # 15 degrés
height_deg = TARGET_BOUNDS[3] - TARGET_BOUNDS[1]  # 15 degrés

# Définir une résolution qui donne une image de taille raisonnable
target_width = 2000  # Largeur cible en pixels
target_height = 2000  # Hauteur cible en pixels

res_lon = width_deg / target_width
res_lat = height_deg / target_height

# Créer l'area definition avec une projection géographique simple
target_area = create_area_def(
    area_id='custom_target_area',
    projection='+proj=longlat +datum=WGS84 +no_defs',
    area_extent=TARGET_BOUNDS,
    resolution=(res_lon, res_lat),  # Résolution en degrés
    units='degrees',
    description='Zone personnalisée 5W-10E 35S-50N'
)

print(f"Zone cible créée: {target_area}")

# Resample SUR LA ZONE REDUITE seulement
print("Resampling sur la zone réduite...")
scn_res = scn.resample(target_area)

vis = scn_res['vis_06'].values.astype('float32')
ir = scn_res['ir_105'].values.astype('float32')

# --- Récupérer les métadonnées de la zone réduite ---
area = scn_res['vis_06'].attrs['area']
crs = area.crs.to_proj4()
extent = area.area_extent
width = area.shape[1]
height = area.shape[0]

# Transformation affine
transform = from_bounds(extent[0], extent[1], extent[2], extent[3], width, height)

print(f"Dimensions réduites: {width}x{height}")
print(f"Zone traitée: {extent}")

# === SUITE DU SCRIPT ORIGINAL ===

# --- VIS normalisé + gamma ---
vis_min, vis_max = np.nanmin(vis), np.nanmax(vis)
vis_norm = (vis - vis_min) / (vis_max - vis_min)
gamma = 1.8
vis_gamma = np.power(vis_norm, 1/gamma)
# --- RGB du visible ---
vis_rgb = np.dstack([vis_gamma]*3)

# --- NOUVELLE PALETTE KELVIN AVEC INTERPOLATION DOUCE ---
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

# Créer la colormap RGB
cmap_kelvin = mcolors.LinearSegmentedColormap.from_list(
    'kelvin_palette_smooth',
    list(zip(np.linspace(0, 1, len(kelvin_values)), colors_kelvin)),
    N=256
)

# Normalizer pour la palette Kelvin
kelvin_min = kelvin_values.min()
kelvin_max = kelvin_values.max()
norm_kelvin = mcolors.Normalize(vmin=kelvin_min, vmax=kelvin_max)

# --- Application de la palette Kelvin à l'IR ---
ir_kelvin = ir
ir_norm = norm_kelvin(ir_kelvin)
ir_norm = np.clip(ir_norm, 0, 1)

# Appliquer la palette RGB
ir_rgb = cmap_kelvin(ir_norm)[..., :3]

# --- CRÉATION DU CANAL ALPHA PROGRESSIF POUR LES TEMPÉRATURES CHAUDES ---
hot_transition_start = 238.15
hot_transition_end = 254.15

alpha_min = 0.0
alpha_max = 1.0

alpha_map = np.ones_like(ir_kelvin)

hot_mask = ir_kelvin >= hot_transition_start
if np.any(hot_mask):
    alpha_norm = (ir_kelvin[hot_mask] - hot_transition_start) / (hot_transition_end - hot_transition_start)
    alpha_norm = np.clip(alpha_norm, 0, 1)
    alpha_map[hot_mask] = alpha_max - (alpha_max - alpha_min) * alpha_norm

very_hot_mask = ir_kelvin >= hot_transition_end
alpha_map[very_hot_mask] = alpha_min

ir_rgb = np.where(np.isnan(ir_rgb), 0, ir_rgb)
alpha_map = np.where(np.isnan(ir_kelvin), 0, alpha_map)
alpha_map = np.power(alpha_map, 0.8)

# --- Flou GAUSSIEN ---
BLUR_RADIUS = 10
mask_iso = (ir_kelvin >= 250.15) & (ir_kelvin <= 253.15)

ir_rgb_masked = np.zeros_like(ir_rgb, dtype=np.float32)
ir_rgb_masked[mask_iso] = ir_rgb[mask_iso]

ir_masked_uint8 = (np.clip(ir_rgb_masked, 0, 1) * 255).astype(np.uint8)
im_masked = Image.fromarray(ir_masked_uint8)
im_masked_blur = im_masked.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))
blurred_masked = np.array(im_masked_blur).astype(np.float32) / 255.0

mask_uint8 = (mask_iso.astype(np.uint8) * 255)
im_mask = Image.fromarray(mask_uint8)
im_mask_blur = im_mask.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))
mask_blur = (np.array(im_mask_blur).astype(np.float32) / 255.0)[..., None]

ir_rgb_smoothed = ir_rgb * (1.0 - mask_blur) + blurred_masked * mask_blur
ir_rgb = ir_rgb_smoothed

# --- FUSION SANDWICH ---
sandwich = vis_rgb.copy()
sandwich_multiplicatif = vis_rgb * ir_rgb

IR_BRIGHTNESS = 10
SAT_STRENGTH = 1.4
SHARP_STRENGTH = 0.3

ir_rgb = np.clip(ir_rgb * IR_BRIGHTNESS, 0, 1)
ir_gray = np.mean(ir_rgb, axis=2, keepdims=True)
ir_rgb = np.clip(ir_gray + (ir_rgb - ir_gray) * SAT_STRENGTH, 0, 1)

from scipy.ndimage import gaussian_filter
blur = gaussian_filter(ir_rgb, sigma=3)
ir_rgb = np.clip(ir_rgb + SHARP_STRENGTH * (ir_rgb - blur), 0, 1)

IR_WEIGHT = 0.8
VIS_GAIN = 1.2

vis_rgb = np.clip(vis_rgb * VIS_GAIN, 0, 1)
sandwich = (vis_rgb * (1 - alpha_map[..., np.newaxis])) + (sandwich_multiplicatif * alpha_map[..., np.newaxis] * IR_WEIGHT)

# --- Sauvegarde en GeoTIFF ---
sandwich_tif = (np.clip(sandwich, 0, 1) * 255).astype(np.uint8)
sandwich_tif = np.transpose(sandwich_tif, (2, 0, 1))

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

print("=" * 60)
print("✅ GeoTIFF OPTIMISÉ sauvegardé :", out_tif)
print(f"📏 Dimensions: {width}x{height}")
print(f"🗺️ Zone: 5W-10E 35S-50N")
print("=" * 60) 