from __future__ import division
import numpy as np
import theano
import theano.tensor as T
import PIL.Image
import sys
import pickle
from plas import SdA
from utils import tile_raster_images

model = pickle.load(open(sys.argv[1],'rb'))
outname = sys.argv[2]

sizes = [[(32,32),(16,16)],
         [(16,16),(8,8)],
         [(8,8),(4,4)]]

for layern in range(3):
    last_layer_recons = np.identity(model.dA_layers[layern].n_hidden)
    for k in range(layern,-1,-1):
        da = model.dA_layers[k]
        active = np.zeros((da.n_hidden, da.n_visible))
        for i,row in enumerate(last_layer_recons):
            active[i] = da.get_reconstructed_input( row )
        last_layer_recons = active
        
    image = PIL.Image.fromarray(
        tile_raster_images( X = last_layer_recons,
                            img_shape = (32,32),
                            tile_shape = sizes[layern][1],
                            tile_spacing = (1, 1)))
    image.save('%s_%i.png'%(outname,layern))
