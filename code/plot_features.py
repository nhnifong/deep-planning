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

layern = 0
image = PIL.Image.fromarray(tile_raster_images(X=da.W.get_value(borrow=True).T,
             img_shape=(32, 32), tile_shape=(16, 16),
             tile_spacing=(1, 1)))
image.save('%s_%i.png'%(outname,layern))
