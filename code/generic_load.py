from __future__ import division
import numpy as np
import theano

def load_data(dataset, train_prop=0.8):
    ''' Loads the dataset and divides it into train,test, and validation subsets.

    :type dataset: string
    :param dataset: the path to the dataset (here MNIST)
    '''
    fulldata = np.load(dataset)
    np.random.shuffle(fulldata)

    n_train = int(len(fulldata) * train_prop)
    n_tv = len(fulldata) - n_train
    n_test = int(n_tv * train_prop)
    n_valid = n_tv - n_test
    assert (n_train + n_test + n_valid) == len(fulldata)
    
    train_set = fulldata[:n_train]
    testt_set = fulldata[n_train:n_train+n_test]
    valid_set = fulldata[len(fulldata)-n_valid:]
    
    def shared(shared_x):
        shared_x = theano.shared(np.asarray(data_x, dtype=theano.config.floatX), borrow=borrow)
    
    return map(shared,[train_set, testt_set, valid_set])
