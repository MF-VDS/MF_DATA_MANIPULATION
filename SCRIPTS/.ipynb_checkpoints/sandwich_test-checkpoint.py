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

# ZONE D'INTERET OPTIMISEE : 6W 8E 42N 51N
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

# === CALCUL AUTOMATIQUE DE LA TAILLE POUR 500m DE RÉSOLUTION ===
RESOLUTION_METERS = 500  # Résolution cible en mètres

# Calculer les dimensions en mètres de la zone
# Approximation : 1 degré ≈ 111 km (moyenne)
width_deg = TARGET_BOUNDS[2] - TARGET_BOUNDS[0]  # 14 degrés
height_deg = TARGET_BOUNDS[3] - TARGET_BOUNDS[1]  # 9 degrés

# Conversion en mètres (approximative aux latitudes moyennes)
width_meters = width_deg * 111000  # 1 degré ≈ 111 km
height_meters = height_deg * 111000

# Calcul du nombre de pixels pour 500m de résolution
target_width = int(width_meters / RESOLUTION_METERS)
target_height = int(height_meters / RESOLUTION_METERS)

print(f"Dimensions de la zone: {width_meters/1000:.1f} km x {height_meters/1000:.1f} km")
print(f"Résolution cible: {RESOLUTION_METERS} m")
print(f"Dimensions pixels calculées: {target_width} x {target_height}")

# Calcul de la résolution en degrés pour cette taille
res_lon = width_deg / target_width
res_lat = height_deg / target_height

target_area = create_area_def(
    area_id='custom_target_area',
    projection='+proj=longlat +datum=WGS84 +no_defs',
    area_extent=TARGET_BOUNDS,
    resolution=(res_lon, res_lat),
    units='degrees',
    description=f'Zone personnalisée 6W-8E 42N-51N - {RESOLUTION_METERS}m'
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

transform = from_bounds(extent[0], extent[1], extent[2], extent[3], width, height)

print(f"=== CHIFFRES OPTIMISES ===")
print(f"Dimensions réduites: {width}x{height}")
print(f"Zone traitée: {extent}")
print(f"Résolution effective: {width_meters/width/1000:.1f} km x {height_meters/height/1000:.1f} km")

# === SCRIPT SIMPLIFIÉ ===

# --- VIS normalisé + gamma ---
vis_min, vis_max = np.nanmin(vis), np.nanmax(vis)
vis_norm = (vis - vis_min) / (vis_max - vis_min)
gamma = 1.8
vis_gamma = np.power(vis_norm, 1/gamma)
# --- RGB du visible ---
vis_rgb = np.dstack([vis_gamma]*3)

# ===================================================================
# === SAUVEGARDE DU VISIBLE SEUL ===
# ===================================================================

# --- Préparer le visible ---
vis_uint8 = (np.clip(vis_rgb, 0, 1) * 255).astype(np.uint8)
vis_uint8 = np.transpose(vis_uint8, (2, 0, 1))  # (3, height, width)

# --- Sauvegarde du visible seul ---
out_vis = os.path.join(output, "vis.tif")

with rasterio.open(
    out_vis,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=3,
    dtype=np.uint8,
    crs=crs,
    transform=transform,
) as dst:
    dst.write(vis_uint8)

print("✅ Visible seul sauvegardé :", out_vis)

# --- PALETTE KELVIN ---
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
]) / 255.0

cmap_kelvin = mcolors.LinearSegmentedColormap.from_list(
    'kelvin_palette_smooth',
    list(zip(np.linspace(0, 1, len(kelvin_values)), colors_kelvin)),
    N=256
)

kelvin_min = kelvin_values.min()
kelvin_max = kelvin_values.max()
norm_kelvin = mcolors.Normalize(vmin=kelvin_min, vmax=kelvin_max)

# --- Application de la palette Kelvin à l'IR ---
ir_kelvin = ir
ir_norm = norm_kelvin(ir_kelvin)
ir_norm = np.clip(ir_norm, 0, 1)
ir_rgb = cmap_kelvin(ir_norm)[..., :3]

# --- CANAL ALPHA SIMPLE ---
hot_transition_start = 228.15
hot_transition_end = 253.15

alpha_map = np.ones_like(ir_kelvin)
hot_mask = ir_kelvin >= hot_transition_start
if np.any(hot_mask):
    alpha_norm = (ir_kelvin[hot_mask] - hot_transition_start) / (hot_transition_end - hot_transition_start)
    alpha_norm = np.clip(alpha_norm, 0, 1)
    alpha_map[hot_mask] = 1.0 - alpha_norm

very_hot_mask = ir_kelvin >= hot_transition_end
alpha_map[very_hot_mask] = 0.0

ir_rgb = np.where(np.isnan(ir_rgb), 0, ir_rgb)
alpha_map = np.where(np.isnan(ir_kelvin), 0, alpha_map)

# ===================================================================
# === SAUVEGARDE DE L'IR COLORISÉE SEULE ===
# ===================================================================

# --- Préparer l'IR colorisée avec transparence ---
ir_rgba = np.zeros((height, width, 4), dtype=np.float32)
ir_rgba[..., 0:3] = ir_rgb  # R, G, B
ir_rgba[..., 3] = alpha_map  # Canal Alpha

# Convertir en uint8
ir_rgba_uint8 = (np.clip(ir_rgba, 0, 1) * 255).astype(np.uint8)
ir_rgba_uint8 = np.transpose(ir_rgba_uint8, (2, 0, 1))  # (4, height, width)

# --- Sauvegarde de l'IR colorisée seule ---
out_ir_colorisee = os.path.join(output, "ir_colorisee.tif")

with rasterio.open(
    out_ir_colorisee,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=4,  # 4 canaux : R, G, B, A
    dtype=np.uint8,
    crs=crs,
    transform=transform,
) as dst:
    dst.write(ir_rgba_uint8)

print("✅ IR colorisée seule sauvegardée :", out_ir_colorisee)

# ===================================================================
# === FUSION SANDWICH ===
# ===================================================================

# --- FUSION SANDWICH SIMPLE ---
sandwich_multiplicatif = vis_rgb * ir_rgb
sandwich = (vis_rgb * (1 - alpha_map[..., np.newaxis])) + (sandwich_multiplicatif * alpha_map[..., np.newaxis] * 0.8)

# Post-processing final
sandwich = np.clip(sandwich, 0, 1)

# --- Préparer les données en uint8 ---
sandwich_tif = (np.clip(sandwich, 0, 1) * 255).astype(np.uint8)
sandwich_tif = np.transpose(sandwich_tif, (2, 0, 1))

# --- Sauvegarde en GeoTIFF ---
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
print(f"📏 Dimensions: {width}x{height} pixels")
print(f"🗺️ Zone: 6W-8E 42N-51N")
print(f"📐 Résolution cible: {RESOLUTION_METERS} m")
print("=" * 60)