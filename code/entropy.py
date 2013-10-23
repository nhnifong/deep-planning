from __future__ import division
import numpy as np
import sys
#from generic_load import load_data

image_dataset_path = "/media/Loonies/CrossModal/NumpyArrays/patches_image.npy"
spect_dataset_path = "/media/Loonies/CrossModal/NumpyArrays/patches_spect.npy"

#ims_train, ims_test, ims_valid = load_data(image_dataset_path)


def count_empty(data):
    print data.shape
    l = data.shape[0]
    a = 0
    b = 0
    for i in range(l):
        if sum(data[i])==0:
            a+=1
        else:
            b+=1
    print "Zero vectors: %0.2f" % (100*a/l)
    print "Nonzero vectors: %0.2f" % (100*b/l)

if __name__=="__main__":
    fulldata = np.load(sys.argv[1])
    np.random.shuffle(fulldata)
    count_empty(fulldata[:80000])
