import os
import sys
import glob
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from satpy.scene import Scene
from pyresample import create_area_def
from pyproj import Proj, Transformer
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ============================================================
# === PARAMÈTRES =============================================
# ============================================================

yyyy, mm, dd, hh, minu, minn = sys.argv[1:7]

# Dossier d’entrée (données FCI L1C)
input_dir = f"/stockage/DATA/{yyyy}{mm}{dd}{hh}{minu}0/"
output_dir = "../RESULTS"
os.makedirs(output_dir, exist_ok=True)

# Emprise géographique (en degrés)
lon_min, lat_min = -1, 39
lon_max, lat_max = 11, 44

# Résolution (mètres/pixel)
resolution = 500

# Choix du type de projection pour la reprojection finale
# Options : "ortho" ou "geos"
projection_type = "geos"     # ← change ici si besoin
sat_alt_km = 35786.0          # altitude du satellite pour projection géos

# ============================================================
# === CHARGEMENT DES DONNÉES SATPY ===========================
# ============================================================

scn = Scene(filenames=glob.glob(os.path.join(input_dir, "*.nc")), reader="fci_l1c_nc")
scn.load(["vis_06", "ir_105"])

# ============================================================
# === ZONE DE DÉCOUPE EN LAMBERT AZIMUTAL (fixe) ============
# ============================================================

proj_dict_cut = {
    "proj": "laea",
    "lat_0": 40,
    "lon_0": 5,
    "ellps": "WGS84"
}
proj_cut = Proj(proj_dict_cut)
transformer = Transformer.from_crs("epsg:4326", proj_cut.srs, always_xy=True)
x_min, y_min = transformer.transform(lon_min, lat_min)
x_max, y_max = transformer.transform(lon_max, lat_max)
area_extent_cut = (x_min, y_min, x_max, y_max)

x_size = int((x_max - x_min) / resolution)
y_size = int((y_max - y_min) / resolution)

area_cut = create_area_def(
    area_id="europe_cut",
    description="Zone de découpe Europe",
    projection=proj_dict_cut,
    width=x_size,
    height=y_size,
    area_extent=area_extent_cut,
    units="m"
)

scn_cut = scn.resample(area_cut)
vis = scn_cut["vis_06"].values.astype("float32")
ir = scn_cut["ir_105"].values.astype("float32")

# ============================================================
# === TRAITEMENT VIS + IR ====================================
# ============================================================

# Normalisation VIS + gamma
vis_min, vis_max = np.nanmin(vis), np.nanmax(vis)
vis_norm = (vis - vis_min) / (vis_max - vis_min)
gamma = 2.0
vis_gamma = np.power(vis_norm, 1 / gamma)
vis_rgb = np.dstack([vis_gamma] * 3)

# IR en °C
ir_c = ir - 273.15
mask = ir_c <= -20

# Palette personnalisée
bounds = list(range(-96, -19))
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
cmap_custom = mcolors.ListedColormap(colors)
norm_custom = mcolors.BoundaryNorm(boundaries=bounds, ncolors=len(colors))

ir_rgb = cmap_custom(norm_custom(ir_c))[..., :3]

# Fusion VIS + IR (sandwich multiplicatif)
sandwich = vis_rgb.copy()
sandwich[mask] = vis_rgb[mask] * ir_rgb[mask]

# ============================================================
# === REPROJECTION FINALE (orthographique ou géos) ===========
# ============================================================

if projection_type == "ortho":
    proj_dict_final = {
        "proj": "ortho",
        "lat_0": (lat_min + lat_max) / 2,
        "lon_0": (lon_min + lon_max) / 2,
        "ellps": "WGS84"
    }
elif projection_type == "geos":
    proj_dict_final = {
        "proj": "geos",
        "lon_0": 0,
        "h": sat_alt_km * 1000.0,  # altitude en mètres
        "sweep": "x"
    }
else:
    raise ValueError("projection_type doit être 'ortho' ou 'geos'")

proj_final = Proj(proj_dict_final)
transformer_final = Transformer.from_crs("epsg:4326", proj_final.srs, always_xy=True)
x_min2, y_min2 = transformer_final.transform(lon_min, lat_min)
x_max2, y_max2 = transformer_final.transform(lon_max, lat_max)
area_extent_final = (x_min2, y_min2, x_max2, y_max2)

area_final = create_area_def(
    area_id="final_proj",
    description="Projection finale custom",
    projection=proj_dict_final,
    width=x_size,
    height=y_size,
    area_extent=area_extent_final,
    units="m"
)

scn_final = scn_cut.resample(area_final)
print(f"Projection finale utilisée : {proj_dict_final['proj']}")

# ============================================================
# === SAUVEGARDE EN GeoTIFF ==================================
# ============================================================

area = scn_final["vis_06"].attrs["area"]
crs = area.crs.to_proj4()
extent = area.area_extent
width = area.shape[1]
height = area.shape[0]
transform = from_bounds(extent[0], extent[1], extent[2], extent[3], width, height)

sandwich_tif = (sandwich * 255).astype(np.uint8)
sandwich_tif = np.transpose(sandwich_tif, (2, 0, 1))

out_tif = os.path.join(output_dir, "sandwich_reproj.tif")
with rasterio.open(
    out_tif, "w",
    driver="GTiff",
    height=height,
    width=width,
    count=3,
    dtype=np.uint8,
    crs=crs,
    transform=transform
) as dst:
    dst.write(sandwich_tif)

print("GeoTIFF sauvegardé :", out_tif) 
