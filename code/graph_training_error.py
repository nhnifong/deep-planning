from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt

def read_log(filename):
    """ Given the path to a log file from plas.py, produce an array for each experiment.
        Return the arrays in a dict, keyed by any sane identifier.
        Produce six lists for each experiment, an x and y for each of the three layers.
        x is the epoch indices, y is the normalized reconstruction error.
    """
    data = {}
    expnumber = 0
    epochoffset = 0
    modeoffset = 0
    for line in open(filename):
        line = line[:-1]
        if line.startswith('Experiment'):
            print line
            p1,description = line.split(': ')
            expnumber = int(p1.split(' ')[-1])
            data[expnumber] = {'description':description,
                               'layersizes':[],
                               'layerdata':[]}
            epochoffset = 0
            modeoffset = 0
        elif line.startswith('created dA'):
            sizestr = line.split(' ')[-1]
            sizel1,sizel2 = map(int,sizestr.split('x'))
            data[expnumber]['layersizes'].append(sizel2)
            data[expnumber]['layerdata'].append([{'indices':[],
                                                  'values':[]},
                                                 {'indices':[],
                                                  'values':[]}])
        elif line.startswith('Pre-training'):
            # Pre-training layer 0, epoch 0, cost  175.97775
            pts = line.split()
            layer = int(pts[2][:-1]) #remove comma
            epoch = int(pts[4][:-1]) + epochoffset
            cost = float(pts[-1])
            normcost = cost / data[expnumber]['layersizes'][layer] / 2
            data[expnumber]['layerdata'][layer][modeoffset]['indices'].append(epoch)
            data[expnumber]['layerdata'][layer][modeoffset]['values'].append(normcost)
        elif line.startswith('finished'):
            epochoffset = int(line.split()[1])
            modeoffset += 1
    return data
    
if __name__=='__main__':
    data = read_log(sys.argv[1])
    print data.keys()

    for ep,ls,method in zip([3,4],['-.','-'],['interleaved','layer-wise']):
        
        target = data[ep]['layerdata']
        for lyr,color,ix in zip(target,['magenta','purple','green'],[1,2,3]):
            for k,md in enumerate(lyr):
                line = plt.plot(md['indices'], md['values'])
                label = method+', layer '+str(ix)
                if k!=0: label='_nolegend_'
                plt.setp(line,
                         color=color,
                         linestyle=ls,
                         linewidth=2.0,
                         label=label)
        plt.xlabel('Epochs')
        plt.ylabel('Normalized reconstruction error')
        plt.title("Two methods of Training of a  three-level SdA on spectrograms")
        plt.legend()
        plt.grid(True)
    plt.show()
