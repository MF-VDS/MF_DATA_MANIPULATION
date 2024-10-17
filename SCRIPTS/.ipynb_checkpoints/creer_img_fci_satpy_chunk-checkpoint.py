import os
import sys

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

# Initialise Scene
path_to_chunks = '/chemin_a_indiquer/'+yyyy+mm+dd+'/'

print(os.path.join(path_to_chunks, '*BODY*OPE_'+yyyy+mm+dd+hh+min+'*3?.nc'))

#scn = Scene(filenames=glob.glob(os.path.join(path_to_chunks, 'Mmultic*km*'+yyyy+mm+dd+hh+min+'.nc')), reader='mtg_netcdficare')
scn = Scene(filenames=glob.glob(os.path.join(path_to_chunks, '*BODY*OPE_'+yyyy+mm+dd+hh+min+'*3?.nc')), reader='fci_l1c_nc')
#scn = Scene(filenames=glob.glob(os.path.join(path_to_chunks, '*BODY*OPE_'+yyyy+mm+dd+hh+'0*.nc')), reader='fci_l1c_nc')

# Load a composite
print('load composite')
scn.load([compo], upper_right_corner='NE')

natscn = scn.resample(resampler='native')
#scn.load([compo], upper_right_corner='NE', resolution= resol )
scn.load([compo], upper_right_corner='NE')

print('save_dataset')
natscn.save_dataset(compo, filename='./'+compo+'_'+ yyyy+mm+dd+'_'+hh+min+'0_satpy'+'.tif')

#scn.show('true_color')
