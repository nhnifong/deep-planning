from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

data = [
    [3.4295983886718751, 3.5137575683593751, 3.3684912109375, 3.4133918457031251, 3.1713857421874998, 3.2470227050781251],
    [3.12874267578125, 3.1378144531249998, 3.1317307128906249, 3.0916447753906251, 2.9373598632812499, 2.9984077148437498],
    [6.0462534179687504, 6.7274531250000003, 6.8281245117187499, 6.4565893554687497, 6.3681079101562501, 7.0638442382812503],
    [5.4855, 5.5356679687500003, 5.5058818359375001, 5.74357373046875, 5.7712841796875001, 5.5481762695312504],
    [3.5233041992187499, 3.3359489746093751, 3.2895532226562501, 3.1626972656249999, 3.3691701660156248, 3.246654052734375],
    [3.207746337890625, 3.2596235351562499, 3.2455019531249998, 3.0711311035156248, 3.1341501464843748, 3.1543505859374998],
    [3.6638259277343752, 3.8319042968749999, 3.765566162109375, 3.6108095703125, 3.7537172851562501, 3.62643408203125],
    [3.4441669921875002, 3.5919899902343748, 3.398116943359375, 3.2619775390624999, 3.3315288085937498, 3.2573664550781252]
]

def df(a,b):
    """ calculate the degrees of freedom in a two-sample t test. a and b are lists of samples. """
    n1 = len(a)
    n2 = len(b)
    s1 = np.std(a)
    s2 = np.std(b)
    n = (s1**2/n1 + s2**2/n2)**2
    d1 = (s1**2/n1)**2 / (n1-1)
    d2 = (s2**2/n2)**2 / (n2-2)
    return n/(d1+d2)

def tstat(a,b):
    """ Calculate the two-sample t test. a and b are lists of samples"""
    n1 = len(a)
    n2 = len(b)
    s1 = np.std(a)
    s2 = np.std(b)
    x1 = np.mean(a)
    x2 = np.mean(b)
    return (x1-x2)/(s1**2/n1 + s2**2/n2)**0.5

print "df = " + str(df(data[4],data[5]))
print "t = " + str(tstat(data[4],data[5]))

# generate a boxplot figure to compare the values
plt.boxplot(data, notch=False, sym='+', vert=True, whis=1.5)
plt.grid(True)
plt.xlabel('Experiment')
plt.ylabel('Reconstruction Error')
plt.title("Distributions of test set reconstruction error for each experiment for 20 random seeds")

plt.show()
