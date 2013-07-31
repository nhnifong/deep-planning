import sys
import numpy as np
from sklearn.decomposition import RandomizedPCA
import time

infile = sys.argv[1]
outfile = sys.argv[2]
dim = int(sys.argv[3])

X = np.load(infile)
print X.shape

began = time.clock()
pca = RandomizedPCA(n_components=dim, whiten=True)
pca.fit(X)
print(pca.explained_variance_ratio_)
Y = pca.transform(X)
print Y.shape
np.save(outfile, Y)
print time.clock()-began
