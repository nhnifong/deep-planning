from __future__ import division

import sys
import time

import numpy
import theano
import theano.tensor as T
from theano.tensor.shared_randomstreams import RandomStreams

from generic_load import load_data
from mlp import HiddenLayer
from dA import dA

class SdA(object):
    """
    Stacked denoising autoencoder
    layer-sizes: a list of integers indicating the width of each hidden layer
    """
    def __init__(self,numpy_rng, n_ins, layer_sizes, corruption_levels=[0.5, 0.5]):
        self.sigmoid_layers = []
        self.dA_layers = []
        self.params = []
        self.n_layers = len(layer_sizes)
        self.x = T.matrix('x')
        
        theano_rng = RandomStreams(numpy_rng.randint(2 ** 30))

        for i in xrange(self.n_layers):
            if i==0:
                input_size = n_ins
                layer_input = self.x
            else:
                input_size = layer_sizes[i]
                layer_input = self.sigmoid_layers[-1].output
    
            sigmoid_layer = HiddenLayer(rng        = numpy_rng,
                                        input      = layer_input,
                                        n_in       = input_size,
                                        n_out      = layer_sizes[i],
                                        activation = T.nnet.sigmoid)
            self.sigmoid_layers.append(sigmoid_layer)
            self.params.extend(sigmoid_layer.params)
            
            dA_layer = dA(numpy_rng  = numpy_rng,
                          theano_rng = theano_rng,
                          input      = layer_input,
                          n_visible  = input_size,
                          n_hidden   = layer_sizes[i],
                          W          = sigmoid_layer.W,
                          bhid       = sigmoid_layer.b)
            self.dA_layers.append(dA_layer)

            

    def train(data, max_runtime, max_epochs, layer_wise = False):
        began = time.clock()
        epochs = 0
        while (time.clock()-began) < max_runtime and epochs < max_epochs :
            print avg_reconstruction_error
            #minimise reconstruction error on data[epochs]
            epochs += 1
        print "finished %i epochs in %0.1f seconds" % (epochs, (time.clock()-began))

    def test(data):
        pass

def experiment():
    image_dataset_path = "/media/Loonies/CrossModal/NumpyArrays/patches_image.npy"
    spect_dataset_path = "/media/Loonies/CrossModal/NumpyArrays/patches_spect.npy"

    print ""
    print "Experiment 1: run ordinary model on images"
    ims_train, ims_test, ims_valid = load_data(image_dataset_path)
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( ims_train, layer_wise=False, max_epochs=10000, max_runtime=7200)
    recon_error = model.test( ims_test )
    print "Average reconstruction error: %0.9f\n" % recon_error

    print ""
    print "Experiment 2: run greedy layer-wise pre-training on images"
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( ims_train, layer_wise=True, max_epochs=10000, max_runtime=7200)
    recon_error = model.test( ims_test )
    print "Average reconstruction error: %0.9f\n" % recon_error

    print ""
    print "Experiment 3: run ordinary model on spectrograms"
    spec_train, spec_test, spec_valid = load_data(spect_dataset_path)
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( spec_train, layer_wise=False, max_epochs=10000, max_runtime=7200)
    recon_error = model.test( spec_test )
    print "Average reconstruction error: %0.9f\n" % recon_error

    print ""
    print "Experiment 4: run greedy layer-wise pre-training on spectrograms"
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( spec_train, layer_wise=True, max_epochs=10000, max_runtime=7200)
    recon_error = model.test( spec_test )
    print "Average reconstruction error: %0.9f\n" % recon_errorprint ""

    # PLASTICITY TESTS

    
