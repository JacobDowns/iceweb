import time
import h5py
import numpy as np
import sys
from pylab import sqrt, linspace
from scipy.interpolate import RectBivariateSpline
from pyproj import Proj
import matplotlib.pyplot as plt

def create_datasets(fileName = '/home/jake/web_data/data/GreenlandData.h5'):
    print("Creating data sets")
    t0 = time.time()

    datasetDict = {}

    dataFile = h5py.File(fileName, 'r')

    
    x = dataFile['x'][:] / 1000.
    y = dataFile['y'][:][::-1] / 1000.

    print(dataFile['y'][:].min(), dataFile['y'][:].max())
    x -= x.min()
    y -= y.min()

    

    dataFile.close()
    velocity = Dataset('velocity',fileName, x, y)
    datasetDict['velocity'] = velocity

    #smb = Dataset('smb',fileName, x, y)
    #datasetDict['smb'] = smb

    bed = Dataset('bed',fileName, x, y)
    datasetDict['bed'] = bed

    surface = Dataset('surface',fileName, x, y)
    datasetDict['surface'] = surface

    thickness = Dataset('thickness',fileName, x, y)
    datasetDict['thickness'] = thickness

    #t2m = Dataset('t2m',fileName, x, y)
    #datasetDict['t2m'] = t2m

    datasetDict['VX'] = Dataset('VX',fileName, x, y)
    datasetDict['VY'] = Dataset('VY',fileName, x, y)

    print("Loaded all data sets in ", time.time() - t0, " seconds")
    return datasetDict



class Dataset:
    def __init__(self, name,fileName, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.data = self.setData(name, fileName)
        self.interp = RectBivariateSpline(self.x, self.y, self.data.T[:,::-1])


    def setData(self, name, fileName):
        dataFile = h5py.File(fileName, 'r')
        if name == 'velocity':
            vx = dataFile['VX'][:]
            vy = dataFile['VY'][:]
            data = sqrt(vx ** 2 + vy ** 2).astype(np.float64)
            dataFile.close()
            return data
        else:
            data = dataFile[name][:]
            dataFile.close()
            return data

    def getInterpolatedValue(self, xs, ys):
        return self.interp(xs, ys)

