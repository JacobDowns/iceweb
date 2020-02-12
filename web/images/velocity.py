from pylab import sqrt, linspace
from scipy.interpolate import RectBivariateSpline
import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import DivergingNorm, LogNorm

'''
Class: Dataset
Argument list: name of dataset, pen type(used for plotting)
Purpose: This is the class of datasets. This will store velocity, smb, etc. This takes the Velocity in X and Y direction
and makes one dataset of just Velocity. This velocity dataset ONLY stores the magnitude but not direction.

Dependencies: pylabs sqrt and linspace, RectBivariateSplint, numpy
Creator: James Stauder
Date created:2/23/18
Last edited: 3/2/18
'''
from palettable.matplotlib import Magma_20
from palettable.matplotlib import Viridis_5
from palettable.scientific.sequential import LaJolla_20



#print(Earth_7.get_mpl_colormap()w(1.))


xs = np.linspace(0., 1., 200)
new_colors = Magma_20.mpl_colormap(xs)
#new_colors = np.delete(colors, [1,2,3,4,5,6,7,8], axis = 0)
print(new_colors)
#quit()
cmap = mpl.colors.LinearSegmentedColormap.from_list(
    'custom_map', new_colors, len(xs))


data = h5py.File('/home/jake/htm_precip_scripts/inputs/data/modern_data/GreenlandData.h5', 'r')



#from PIL import Image
#from matplotlib import cm, colors

fig = plt.figure()
plt.axis('off')
plt.imshow(np.sqrt(data['VX'][:]**2 + data['VY'][:]**2) , cmap=cmap, norm=LogNorm(vmin=2., vmax=3e3))
#plt.colorbar()
#plt.show()
#quit()
#im = Image.fromarray(np.uint8(cm.gist_earth()*255))

fig.savefig('velocity.png', bbox_inches='tight', pad_inches=0, dpi = 1000)


