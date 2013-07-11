from __future__ import division

import numpy
import theano
import theano.tensor as T

"""
Online Deep Belief Network



"""

class HGibbsLayer:
    def __init__(self):
        self.in_shared = []
        self.in_weights = []
        self.activation = []

    def inferencePoint(self):
        """
        read each input vector from it's shared location
        multiply each input vector by it's weight matrix
        compute the error between each transformed input, and the average of all other transformed inputs
        use the error to inform stochasic gradient decent on the weights for that input.
        with the exception of "ground truth" inputs.
        finally, take the average of all weighted inputs and save it as our own activation.
        """
        for X,W in zip(self.in_shared, self.in_weights):
            T.nnet.sigmoid(T.dot(X, W) + self.b)
        
    def registerNewInput(self,hg):
        self.in_shared.append(hg)
        self.in_weights.append( randomWeightMatrix() )

schedule = []


floor = HGibbsLayer()
schedule.append((2,0,floor.inferencePoint))
# takes input from layer1, actual
# runs on even numbered ticks

layer1 = HGibbsLayer()
schedule.append((2,1,layer1.inferencePoint))
# takes input from floor
# runs on odd numbered ticks


# greedy layer-wise training:
#Once a layer has converged....


layer2 = HGibbsLayer()
schedule.append((4,0,layer2.inferencePoint))
# latest act from layer1, and 1 delayed act from same
# runs every 4th tick

layer1.registerNewInput( layer2 )

def start():
    # schedule: for any (tick % rate) + offset, run the registered function
    tick = 0
    while True:
        for (rate,offset,func) in schedule:
            if tick % rate == offset:
                func()
        tick += 1

