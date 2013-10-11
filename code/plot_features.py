from __future__ import division
import numpy as np
import theano
import theano.tensor as T
import PIL.Image
import sys
import os
import pickle
from plas import SdA
from utils import tile_raster_images



sizes = [[(32,32),(16,16)],
         [(16,16),(8,8)],
         [(8,8),(4,4)]]
indir = "models"
outdir = "features"

for fname in os.listdir(indir):

    if not fname.startswith('perlin'): continue

    model = pickle.load(open(os.path.join(indir,fname),'rb'))
    outname = fname[:-4]
    
    for layern in range(3):
        last_layer_recons = np.identity(model.dA_layers[layern].n_hidden)
        for k in range(layern,-1,-1):
            da = model.dA_layers[k]
            active = np.zeros((da.n_hidden, da.n_visible))
            print last_layer_recons
            print last_layer_recons.shape
            for i,row in enumerate(last_layer_recons):
                temp = da.get_reconstructed_input( row ).eval()
                print temp
                print temp.shape
                print active[i].shape
                active[i] = temp
            last_layer_recons = active
            
        image = PIL.Image.fromarray(
            tile_raster_images( X = last_layer_recons,
                                img_shape = (32,32),
                                tile_shape = sizes[layern][1],
                                tile_spacing = (1, 1)))
        image.save(os.path.join(outdir, '%s_%i.png'%(outname,layern)))
