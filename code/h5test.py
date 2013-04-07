import h5py
import numpy

with h5py.File('myfile.hdf5','w') as f:
    dset = f.create_dataset("MyDataset", (100, 100), 'i')
    dset[...] = 42

with h5py.File('myfile.hdf5','r+') as ff:
    nn = ff['MyDataset'][...]
    print nn
