"""
3D render from sandwich.tif

Usage:
    python render_3d_from_sandwich.py /path/to/sandwich.tif output_3d.png
"""

import sys
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LightSource
from PIL import Image
from scipy.ndimage import gaussian_filter

# ---------------------------
# USER PARAMETERS
# ---------------------------
MAX_DIM = 600
COLOR_DIST_THRESHOLD = 0.18
z_exag = 1.0
cam_elev = 40
cam_azim = -60
light_azim = 135
light_altdeg = 45
output_dpi = 200

# ---------------------------
# Kelvin palette
# ---------------------------
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

cmap_kelvin = LinearSegmentedColormap.from_list(
    'kelvin_palette_smooth',
    list(zip(np.linspace(0, 1, len(kelvin_values)), colors_kelvin)),
    N=256
)
lut_rgb = cmap_kelvin(np.linspace(0, 1, 256))[..., :3]
kelvin_min, kelvin_max = kelvin_values.min(), kelvin_values.max()
lut_temps = np.linspace(kelvin_min, kelvin_max, 256)

# ---------------------------
# Helper functions
# ---------------------------
def downsample_rgb(rgb, max_dim):
    h, w = rgb.shape[:2]
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
    new_w, new_h = int(round(w * scale)), int(round(h * scale))
    im = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    im_small = im.resize((new_w, new_h), resample=Image.BILINEAR)
    return np.array(im_small).astype(np.float32) / 255.0, scale

def match_color_to_temp(rgb_pixels, lut_rgb):
    N = rgb_pixels.shape[0]
    temps = np.empty(N, dtype=np.float32)
    dists = np.empty(N, dtype=np.float32)
    chunk = 200000
    for i in range(0, N, chunk):
        px = rgb_pixels[i:i+chunk, None, :]
        diff = px - lut_rgb[None, :, :]
        dist2 = np.sum(diff * diff, axis=2)
        idx = np.argmin(dist2, axis=1)
        temps[i:i+chunk] = lut_temps[idx]
        dists[i:i+chunk] = np.sqrt(dist2[np.arange(len(idx)), idx])
    return temps, dists

# ---------------------------
# Main script
# ---------------------------
if len(sys.argv) < 3:
    print("Usage: python render_3d_from_sandwich.py sandwich.tif output.png")
    sys.exit(1)

sandwich_path = sys.argv[1]
out_png = sys.argv[2]

print(f"Lecture du fichier GeoTIFF : {sandwich_path}")

# Lecture TIFF (conversion manuelle)
with rasterio.open(sandwich_path) as src:
    arr = src.read()  # Ne pas forcer le dtype ici
    arr = arr.astype(np.float32, copy=False)  # conversion manuelle sûre
    rgb = np.transpose(arr, (1, 2, 0))
    rgb = np.clip(rgb / 255.0, 0, 1)
    H, W = rgb.shape[:2]

print(f"Image lue : {W}x{H}")

# Réduction taille pour affichage 3D
rgb_ds, scale = downsample_rgb(rgb, MAX_DIM)
print(f"Downsampled to {rgb_ds.shape[1]}x{rgb_ds.shape[0]}")

# Conversion couleur -> température
flat = rgb_ds.reshape((-1, 3))
temps_flat, dists_flat = match_color_to_temp(flat, lut_rgb)
temps = temps_flat.reshape(rgb_ds.shape[:2])
dists = dists_flat.reshape(rgb_ds.shape[:2])

# Masque IR
ir_mask = dists < COLOR_DIST_THRESHOLD

# Altitude
altitude = np.full_like(temps, 1500.0, dtype=np.float32)
altitude[ir_mask] = (288.15 - temps[ir_mask]) / 0.0065
altitude = np.maximum(altitude, 0.0)
altitude_smooth = gaussian_filter(altitude, sigma=1.0)

# Ombres et lumière
ls = LightSource(azdeg=light_azim, altdeg=light_altdeg)
shaded_rgb = ls.shade_rgb(rgb_ds, altitude_smooth, vert_exag=z_exag)

# Grille de coordonnées
h_ds, w_ds = rgb_ds.shape[:2]
x = np.linspace(0, w_ds-1, w_ds)
y = np.linspace(0, h_ds-1, h_ds)
X, Y = np.meshgrid(x, y)

# Plot 3D
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

step = max(1, int(max(h_ds, w_ds) / 500))
Xs = X[::step, ::step]
Ys = Y[::step, ::step]
Zs = altitude_smooth[::step, ::step] / 1000.0 * z_exag
facecolors = shaded_rgb[::step, ::step, :]

ax.plot_surface(Xs, Ys, Zs, facecolors=facecolors, linewidth=0, antialiased=False, shade=False)
ax.view_init(elev=cam_elev, azim=cam_azim)
ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

fig.savefig(out_png, dpi=output_dpi)
plt.close(fig)
print(f"✅ Image 3D sauvegardée : {out_png}")
