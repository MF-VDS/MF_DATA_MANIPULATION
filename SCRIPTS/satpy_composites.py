import os
import sys
import logging
import warnings  # 1. Importer le module standard de gestion des alertes

# 2. Bloquer les avertissements "invalid value encountered" de NumPy/Dask
import numpy as np
np.seterr(invalid='ignore')
# Bloquer les warnings Python standards
warnings.filterwarnings("ignore")

# 3. Filtrer les messages textuels spécifiques de Satpy et des formats sous-jacents
warnings.filterwarnings("ignore", message="invalid value encountered in cast")
warnings.filterwarnings("ignore", message="No sensor name specified in HDF5 file")
warnings.filterwarnings("ignore", message="The following datasets were not created and may require resampling")
# Forcer le système de logs à n'afficher que les ERREURS (masque les INFO et WARNING)
logging.basicConfig(level=logging.ERROR)
logging.getLogger("satpy").setLevel(logging.ERROR)
logging.getLogger("pyresample").setLevel(logging.ERROR)

# --- Le reste de vos imports reste inchangé ---
import hdf5plugin
from satpy import Scene
import glob
from pyresample import create_area_def

compo=sys.argv[1]
yyyy=sys.argv[2]
mm=sys.argv[3]
dd=sys.argv[4]
hh=sys.argv[5]
min=sys.argv[6]
varres=sys.argv[7]
resol=int(varres)

# Initialise Path
path_to_chunks = '/home/coster/DATA/'+yyyy+mm+dd+'/'

print(os.path.join(path_to_chunks, '*.nc'))

# 1. Initialisation propre de la scène
files = glob.glob(os.path.join(path_to_chunks, '*.nc'))
if not files:
    print(f"Erreur : Aucun fichier trouvé dans {path_to_chunks}")
    sys.exit(1)

scn = Scene(filenames=files, reader='fci_l1c_nc')

# 2. CHARGEMENT D'ABORD
# C'est cette étape qui extrait les métadonnées géographiques (areas)
print('load composite')
scn.load([compo], upper_right_corner='NE')

# 3. RÉÉCHANTILLONNAGE ENSUITE
# Maintenant que le dataset est chargé, 'native' peut analyser les "areas"
print('resample native')
natscn = scn.resample(resampler='native')

# 4. SAUVEGARDE SUR LA SCÈNE RÉÉCHANTILLONNÉE
print('save_dataset')
# On utilise 'natscn' ici pour exporter le résultat du rééchantillonnage
natscn.save_dataset(compo, filename='../RESULTS/'+compo+'_'+ yyyy+mm+dd+'_'+hh+min+'0_mtgi1_satpy'+'.tif')
