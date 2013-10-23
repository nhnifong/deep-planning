from __future__ import division
import sys
import numpy as np
import matplotlib.pyplot as plt

a_data = eval(open(sys.argv[1]).readline())

reorder = [0,5,1,7,2,4,3,6]

data = []
for k in reorder:
    data.append(a_data[k])
    print len(a_data[k])

def lsmd(sample):
    return {'len':len(sample), 'std':np.std(sample), 'mean':np.mean(sample)}

# TODO change these two functions to take a pair of LSM dicts instead
def df(a,b):
    """ calculate the degrees of freedom in a two-sample t test. a and b are the lsm dicts from lists of samples """
    n = (a['std']**2/a['len'] + b['std']**2/b['len'])**2
    d1 = (a['std']**2/a['len'])**2 / (a['len']-1)
    d2 = (b['std']**2/b['len'])**2 / (b['len']-2)
    return n/(d1+d2)

def tstat(a,b):
    """ Calculate the two-sample t test. a and b are the lsm dicts from lists of samples"""
    return (a['mean']-b['mean'])/(a['std']**2/a['len'] + b['std']**2/b['len'])**0.5
    
def difflsm(lsm1, lsm2):
    """ Calculate the length, standard deviation, and mean of the distribution of differences between two samples
    Given the lenth, standard deviations, and means of each of those two samples. """
    diff = {}
    diff['mean'] = a['mean'] - b['mean']
    diff['std'] = ( a['std']/a['len'] + b['std']/b['len'] )**0.5
    assert a['len'] == b['len']
    diff['len'] = a['len']
    return diff

for i,j in [(0,1),(2,3),(4,5),(6,7)]:
    print "\nDifference between experiment %i and %i" % (i,j)
    a = lsmd(data[i])
    b = lsmd(data[j])
    print "mean1 - mean2 = %0.5f" % (a['mean']-b['mean'])
    print "df = " + str(df(a,b))
    print "t = " + str(tstat(a,b))
    
print '\n ----------------'

for i,j,k,l in [(0,1,2,3),(4,5,6,7)]:
    diff1 = difflsm( lsmd(data[i]), lsmd(data[j]) )
    diff2 = difflsm( lsmd(data[k]), lsmd(data[l]) )
    print "\n(e%i - e%i) - (e%i - e%i)" % (i,j,k,l)
    a = lsmd(data[i])
    b = lsmd(data[j])
    print "mean1 - mean2 = %0.5f" % (a['mean']-b['mean'])
    print "df = " + str(df(a,b))
    print "t = " + str(tstat(a,b))

# generate a boxplot figure to compare the values
plt.boxplot(data, notch=False, sym='+', vert=False, whis=1.5)
plt.grid(True)
plt.axis([2.5, 17.5, 8.5, 0.5])
plt.ylabel('Experiment')
plt.xlabel('Reconstruction Error')
plt.title("Test set reconstruction error for each experiment; 20 random seeds")

plt.text(4.1, 0.9, 'Interleaved model on images only')
plt.text(4.1, 1.9, 'Interleaved model on audio, then images')

plt.text(4.1, 2.9, 'Layer-wise model on images only')
plt.text(4.1, 3.9, 'Layer-wise model on audio, then images')

plt.text(3.0, 4.9, 'Interleaved model on audio only')
plt.text(4.1, 5.9, 'Interleaved model on images, then audio')

plt.text(3.0, 6.9, 'Layer-wise model on audio only')
plt.text(4.1, 7.9, 'Layer-wise model on images, then audio')





plt.show()



