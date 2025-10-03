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
from pyresample import create_area_def

os.environ['PATH'] = f"/opt/conda/env_MF_teledetection/bin:{os.environ['PATH']}" 
os.environ['PATH'] = f"~/.conda/envs/env_MF_teledetection/bin:{os.environ['PATH']}"
os.environ['GDAL_DATA'] = '/opt/conda/env_MF_teledetection/share/gdal'
os.environ['PROJ_LIB'] = '/opt/conda/env_MF_teledetection/share/proj'



from pyresample import create_area_def

# Projection Lambert azimutal équivalent, centrée sur l’Europe
proj_dict = {
    'proj': 'laea',
    'lat_0': 46,    # latitude du centre
    'lon_0': 2,    # longitude du centre
    'ellps': 'WGS84'
}

# Étendue en mètres : (xmin, ymin, xmax, ymax)
# Ici environ Europe de l’Ouest
area_extent = (-2500000, -2000000, 2500000, 2500000)

# Résolution en mètres
resolution = 500
x_size = int((area_extent[2] - area_extent[0]) / resolution)
y_size = int((area_extent[3] - area_extent[1]) / resolution)

# Définition de l’aire
area_def = create_area_def(
    area_id="europe_western",   # identifiant (ok en texte)
    description="Europe Western",  # description (texte libre)
    projection=proj_dict,
    width=x_size,
    height=y_size,
    area_extent=area_extent,
    units="m"
)



shell=True

yyyy=sys.argv[1]
mm=sys.argv[2]
dd=sys.argv[3]
hh=sys.argv[4]
min=sys.argv[5]
minn=sys.argv[6]


#input = '/stockage/DATA/'+yyyy+mm+dd+hh+min+'0/' #plein disque
#input = '/stockage/DATA/'+yyyy+mm+dd+hh+min+'0_HR/' # plein disque HR
input = '/stockage/DATA/'+yyyy+mm+dd+hh+min+'0/'  # chunk 30/39 HR # plus rapide sur l'Europe



download_dir = os.path.join(os.getcwd(), "../RESULTS")
os.makedirs(download_dir, exist_ok=True)

output = '../RESULTS'

reader_to_use = "fci_l1c_nc"

filename = (output + '/RGB_sadnwich' )

#myfiles = find_files_and_readers(base_dir=input,
#                                 start_time=datetime(yyyy,mm,dd,hh,min),
#                                 end_time=datetime(yyyy,mm,dd,hh,minn),
#                                 reader=reader_to_use)

# Charger les données
#scn = Scene(filenames=myfiles, reader='fci_l1c_nc')
scn = Scene(filenames=glob.glob(os.path.join(input, '*.nc')), reader='fci_l1c_nc')

# --- Chargement des données ---
scn.load(['vis_06', 'ir_105'])

#scn_res = scn.resample(scn['vis_06'].area)
# Resampling de la scène
scn_res = scn.resample(area_def) 


vis = scn_res['vis_06'].values.astype('float32')
ir  = scn_res['ir_105'].values.astype('float32')

##test ajout gamma seulement au vis 06
## --- Normalisation VIS ---
#vis_min, vis_max = np.nanmin(vis), np.nanmax(vis)
#vis_norm = (vis - vis_min) / (vis_max - vis_min)
## --- Correction gamma (uniquement sur le VIS) ---
#gamma = 2.0
#vis_norm = np.power(vis_norm, 1/gamma)
## RGB du visible (éclairci)
#vis_rgb = np.dstack([vis_norm]*3) 


# --- VIS normalisé + gamma ---
vis_min, vis_max = np.nanmin(vis), np.nanmax(vis)
vis_norm = (vis - vis_min) / (vis_max - vis_min)
gamma = 2.0
vis_gamma = np.power(vis_norm, 1/gamma)
# --- RGB du visible ---
vis_rgb = np.dstack([vis_gamma]*3)

# --- IR en °C ---
ir_c = ir - 273.15
mask = ir_c <= -20


##################################################################Si palette standard, décommenter les lignes suivantes
## --- Conversion IR en °C ---
#ir_c = ir - 273.15
## --- Masque IR ---
#mask = ir_c <= -20  # True = zones à coloriser

## --- Normalisation IR pour la palette ---
#if np.any(mask):
#    ir_min, ir_max = np.nanmin(ir_c[mask]), np.nanmax(ir_c[mask])
#    ir_norm = (ir_c - ir_min) / (ir_max - ir_min)
#    ir_norm = np.clip(ir_norm, 0, 1)
#else:
##    ir_norm = np.zeros_like(ir_c)
#
## --- Application de la palette ---
#cmap = plt.get_cmap("RdBu_r")  #jet, turbo, RdBu_r, inferno
#ir_rgb = cmap(ir_norm)[..., :3]
########################################################## fin palette standard


##################################################################Si palette à façon # Commenter ou décommenter
# --- Définition des bornes et couleurs à partir de ta table ---
bounds = list(range(-96, -19))  # de -96 à -20 inclus
colors = [
    "#aa8cff","#b286ff","#ba80ff","#c27aff","#ca74ff","#d26eff","#db7efe",
    "#e48efd","#ed9efc","#f6aefb","#ffbefa","#f2b8ea","#e5b2da","#d8acca",
    "#cba6ba","#bea0aa","#a8868a","#926c6a","#7c524a","#66382a","#501e0a",
    "#601915","#701420","#800f2c","#900a37","#a10543","#ab1145","#b61d47",
    "#c12949","#cc354b","#d7414e","#dd4a4c","#e3544a","#e95e48","#ef6846",
    "#f57244","#f67e49","#f88a4f","#f99655","#fba25b","#fdaf61","#fdb969",
    "#fdc372","#fdcd7b","#fdd784","#fee18d","#fde696","#fdec9f","#fdf2a8",
    "#fdf8b1","#fdfebb","#f7fcb4","#f2faad","#edf8a6","#e8f69f","#e3f498",
    "#d7ef9a","#cbea9c","#bfe59f","#b3e0a1","#a7dca4","#9ad6a4","#8dd1a4",
    "#80cca4","#73c7a4","#67c2a5","#5ab7aa","#4eacaf","#41a1b4","#3596b9",
    "#298cbe","#3280b9","#3c75b4","#4669af","#505eaa","#5a53a5"
]
#  ][::-1]  # inversé car ta table va de -20 vers -96  # si besoin d 'inversé

# --- Création colormap + normalisation ---
cmap_custom = mcolors.ListedColormap(colors)
norm_custom = mcolors.BoundaryNorm(boundaries=bounds, ncolors=len(colors))

# --- Application à l'IR ---
ir_c = ir - 273.15  # en °C
mask = ir_c <= -20

# Appliquer palette seulement sur mask
ir_rgb = cmap_custom(norm_custom(ir_c))[..., :3] 
########################################################## fin palette à façon


# --- Superposition IR sur le visible seulement là où mask=True ---
#ajout transparence
#alpha_ir = 0.85  # 0 = IR invisible, 1 = IR opaque, exmeple 0.6 = 60% d IR
#sandwich = vis_rgb.copy()
#sandwich[mask] = (
#    (1 - alpha_ir) * vis_rgb[mask] + alpha_ir * ir_rgb[mask]
#)

# --- Fusion type "sandwich multiplicatif" ---
# Ici on multiplie la luminance VIS par la couleur IR
sandwich = vis_rgb * ir_rgb

# Appliquer que là où mask=True
sandwich = vis_rgb.copy()
sandwich[mask] = vis_rgb[mask] * ir_rgb[mask] 



# --- Retour vertical si besoin ---
#sandwichflip = np.flipud(sandwich)
# --- Sauvegarde ---
#plt.imsave("../RESULTS/sandwichflip.png", sandwichflip)

# mettre les 2 sur la grille IR
#scn_res = scn.resample(scn['vis_06'].area) # test rc pour ressampler
scn_res = scn.resample(scn['vis_06'].area)
# --- Récupérer zone géographique de la donnée ---
area = scn_res['ir_105'].attrs['area']
crs = area.crs.to_proj4()  # projection de la zone
extent = area.area_extent   # (xmin, ymin, xmax, ymax)
width = area.shape[1]
height = area.shape[0]

# Transformation affine
transform = from_bounds(extent[0], extent[1], extent[2], extent[3], width, height)

# --- Préparer les données en uint8 ---
sandwich_tif = (sandwich * 255).astype(np.uint8)
sandwich_tif = np.transpose(sandwich_tif, (2, 0, 1))  # (bands, height, width)

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

print(" GeoTIFF sauvegardé :", out_tif) 
