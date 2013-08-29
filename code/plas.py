
from __future__ import division

import sys
import os
import time
import pickle

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
        self.corruption_levels = corruption_levels
        self.sigmoid_layers = []
        self.dA_layers = []
        self.params = []
        self.n_layers = len(layer_sizes)
        self.x = T.matrix('x')
        self.numpy_rng = numpy_rng
        
        theano_rng = RandomStreams(numpy_rng.randint(2 ** 30))

        for i in xrange(self.n_layers):
            if i==0:
                input_size = n_ins
                layer_input = self.x
            else:
                input_size = layer_sizes[i-1]
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
            print "created dA %ix%i" % (input_size, layer_sizes[i])

    def pretraining_functions(self, train_set_x, batch_size):
        # index to a [mini]batch                                                      
        index = T.lscalar('index')  # index to a minibatch                            
        corruption_level = T.scalar('corruption')  # % of corruption to use           
        learning_rate = T.scalar('lr')  # learning rate to use                        
        # number of batches                                                           
        n_batches = train_set_x.get_value(borrow=True).shape[0] / batch_size
        # begining of a batch, given `index`                                          
        batch_begin = index * batch_size
        # ending of a batch given `index`                                             
        batch_end = batch_begin + batch_size

        pretrain_fns = []
        for dA in self.dA_layers:
            # get the cost and the updates list
            cost, updates = dA.get_cost_updates(corruption_level, learning_rate)
            # compile the theano function                                             
            fn = theano.function(inputs=[index,
                              theano.Param(corruption_level, default=0.2),
                              theano.Param(learning_rate, default=0.1)],
                                 outputs=cost,
                                 updates=updates,
                                givens={self.x: train_set_x[batch_begin:
                                                             batch_end]})
            # append `fn` to the list of functions                                    
            pretrain_fns.append(fn)

        return pretrain_fns

    def train(self, train_set_x, max_epochs=1000, max_runtime=7200, layer_wise=False, batch_size=16):

        # just notices that max_runtime is broken. Some operation tool a negative amount of time. Probably for the better :/

        pretrain_lr = 0.001

        # compute number of minibatches for training, validation and testing
        n_train_batches = train_set_x.get_value(borrow=True).shape[0]
        n_train_batches = int(n_train_batches / batch_size)

        # random seed used to reproduce experiments
        self.numpy_rng = numpy.random.RandomState(72723)

        print "Creating Theano pre-training functions"
        pretraining_fns = self.pretraining_functions(train_set_x=train_set_x,
                                                    batch_size=batch_size)
        
        print "Starting the training clock now. Training will stop after %i epochs or %0.2f hours, whichever is sooner" % (max_epochs, max_runtime/3600)
        began = time.clock()
        # divide the max epochs evenly between layers
        # if layer_wise, train all of a layer before the next, else interleave
        layer_index = 0
        epoch_counter = 0
        while (time.clock()-began) < max_runtime and epoch_counter < max_epochs :
            c = []
            for batch_index in xrange(n_train_batches):
                c.append(pretraining_fns[layer_index](index=batch_index,
                              corruption=self.corruption_levels[layer_index],
                              lr=pretrain_lr))
            print 'Pre-training layer %i, epoch %d, cost ' % (layer_index, epoch_counter),
            print numpy.mean(c)

            epoch_counter += 1
            if layer_wise:
                layer_index = (epoch_counter * self.n_layers // max_epochs)
            else:
                layer_index = epoch_counter % self.n_layers
        print "finished %i epochs in %0.1f seconds" % (epoch_counter, (time.clock()-began))

    def test(self, test_set_x):
        # compute average reconstruction error on test set
        index = T.lscalar('index')
        corruption_level = T.scalar('corruption')
        learning_rate = T.scalar('lr')
        batch_size = 16
        batch_begin = index * batch_size
        batch_end = batch_begin + batch_size
        # get cost for last dA in list
        cost, updates = self.dA_layers[-1].get_cost_updates(corruption_level, learning_rate)
        # test function that must be iterated over minbatches
        test_fn = theano.function(inputs=[index,
                                          theano.Param(corruption_level, default=0.2),
                                          theano.Param(learning_rate, default=0.1)],
                                  outputs=cost,
                                  updates=updates,
                                  givens={self.x: test_set_x[batch_begin:
                                                                 batch_end]})
               
        n_train_batches = test_set_x.get_value(borrow=True).shape[0]
        n_train_batches = int(n_train_batches / batch_size)
        
        c = []
        for batch_index in xrange(n_train_batches):
            c.append(test_fn(index=batch_index,
                             corruption=self.corruption_levels[-1],
                             lr=0.0))
        return numpy.mean(c)


image_dataset_path = "/media/Loonies/CrossModal/NumpyArrays/patches_image.npy"
spect_dataset_path = "/media/Loonies/CrossModal/NumpyArrays/patches_spect.npy"
model_save_dir = "/media/Loonies/CrossModal/Models/"

numpy_rng = numpy.random.RandomState(89677) #89677
numpy_rng = numpy.random.RandomState(89678)

def controlgrp():

    print ""
    print "Experiment 1: run ordinary model on images"
    ims_train, ims_test, ims_valid = load_data(image_dataset_path)
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( ims_train, max_epochs=1000, max_runtime=7200, layer_wise=False)
    save_path = os.path.join(model_save_dir, "interleaved_images_only.sda")
    print "Training complete, saving model at %s" % save_path
    pickle.dump(model,open(save_path,'wb'))
    recon_error = model.test( ims_test )
    print "Average reconstruction error: %0.9f\n" % recon_error

    print ""
    print "Experiment 2: run greedy layer-wise pre-training on images"
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( ims_train, max_epochs=1000, max_runtime=7200, layer_wise=True)
    save_path =os.path.join(model_save_dir, "layerwise_images_only.sda")
    print "Training complete, saving model at %s" % save_path
    pickle.dump(model,open(save_path,'wb'))
    recon_error = model.test( ims_test )
    print "Average reconstruction error: %0.9f\n" % recon_error

    print ""
    print "Experiment 3: run ordinary model on spectrograms"
    spec_train, spec_test, spec_valid = load_data(spect_dataset_path)
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( spec_train, max_epochs=1000, max_runtime=7200, layer_wise=False)
    save_path =os.path.join(model_save_dir, "interleaved_spect_only.sda")
    print "Training complete, saving model at %s" % save_path
    pickle.dump(model,open(save_path,'wb'))
    recon_error = model.test( spec_test )
    print "Average reconstruction error: %0.9f\n" % recon_error

def special():
    spec_train, spec_test, spec_valid = load_data(spect_dataset_path)
    print ""
    print "Experiment 4: run greedy layer-wise pre-training on spectrograms"
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( spec_train, max_epochs=1000, max_runtime=7200, layer_wise=True)
    save_path =os.path.join(model_save_dir, "layerwise_spect_only.sda")
    print "Training complete, saving model at %s" % save_path
    pickle.dump(model,open(save_path,'wb'))
    recon_error = model.test( spec_test )
    print "Average reconstruction error: %0.9f\n" % recon_error
    print ""


# PLASTICITY TESTS
def experiment():

    ims_train, ims_test, ims_valid = load_data(image_dataset_path)
    spec_train, spec_test, spec_valid = load_data(spect_dataset_path)

    print ""
    print "Experiment 5: train interleaved model on images, then spectrograms"
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( ims_train, max_epochs=500, max_runtime=7200, layer_wise=False)
    model.train( spec_train, max_epochs=500, max_runtime=7200, layer_wise=False)
    save_path = os.path.join(model_save_dir, "interleaved_images_then_spec.sda")
    print "Training complete, saving model at %s" % save_path
    pickle.dump(model,open(save_path,'wb'))
    recon_error = model.test( spec_test )
    print "Average reconstruction error on spectrograms: %0.9f" % recon_error
    recon_error = model.test( ims_test )
    print "Average reconstruction error on images: %0.9f\n" % recon_error

    print ""
    print "Experiment 6: train interleaved model on spectrograms, then images"
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( spec_train, max_epochs=500, max_runtime=7200, layer_wise=False)
    model.train( ims_train, max_epochs=500, max_runtime=7200, layer_wise=False)
    save_path = os.path.join(model_save_dir, "interleaved_spec_then_images.sda")
    print "Training complete, saving model at %s" % save_path
    pickle.dump(model,open(save_path,'wb'))
    recon_error = model.test( spec_test )
    print "Average reconstruction error on spectrograms: %0.9f" % recon_error
    recon_error = model.test( ims_test )
    print "Average reconstruction error on images: %0.9f\n" % recon_error

    print ""
    print "Experiment 7: train layer-wise model on images, then spectrograms"
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( ims_train, max_epochs=500, max_runtime=7200, layer_wise=True)
    model.train( spec_train, max_epochs=500, max_runtime=7200, layer_wise=True)
    save_path = os.path.join(model_save_dir, "layerwise_images_then_spec.sda")
    print "Training complete, saving model at %s" % save_path
    pickle.dump(model,open(save_path,'wb'))
    recon_error = model.test( spec_test )
    print "Average reconstruction error on spectrograms: %0.9f" % recon_error
    recon_error = model.test( ims_test )
    print "Average reconstruction error on images: %0.9f\n" % recon_error

    print ""
    print "Experiment 8: train layer-wise model on spectrograms, then images"
    model = SdA( numpy_rng, 1024, [256,64,16], [0.3,0.3,0.3] )
    model.train( spec_train, max_epochs=500, max_runtime=7200, layer_wise=True)
    model.train( ims_train, max_epochs=500, max_runtime=7200, layer_wise=True)
    save_path = os.path.join(model_save_dir, "layerwise_spec_then_images.sda")
    print "Training complete, saving model at %s" % save_path
    pickle.dump(model,open(save_path,'wb'))
    recon_error = model.test( spec_test )
    print "Average reconstruction error on spectrograms: %0.9f" % recon_error
    recon_error = model.test( ims_test )
    print "Average reconstruction error on images: %0.9f\n" % recon_error


   
if __name__ == "__main__":
    special()
    #controlgrp()
    #experiment()
