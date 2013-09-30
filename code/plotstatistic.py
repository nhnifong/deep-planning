from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

a_data = [[3.4295983886718751, 3.5137575683593751, 3.3684912109375, 3.4133918457031251, 3.1713857421874998, 3.2470227050781251, 3.2949992675781248, 3.189135009765625, 3.360404052734375, 3.3626188964843751, 3.3320600585937501], [3.12874267578125, 3.1378144531249998, 3.1317307128906249, 3.0916447753906251, 2.9373598632812499, 2.9984077148437498, 3.1559890136718751, 2.9389067382812502, 3.0454946289062499, 3.0450339355468752, 3.110087890625], [6.0462534179687504, 6.7274531250000003, 6.8281245117187499, 6.4565893554687497, 6.3681079101562501, 7.0638442382812503, 6.8915253906249996, 6.7130732421874999, 7.0103115234375002, 6.8936870117187503, 6.8536479492187503], [5.4855, 5.5356679687500003, 5.5058818359375001, 5.74357373046875, 5.7712841796875001, 5.5481762695312504, 5.4730361328125001, 5.2956533203124998, 5.7262172851562498, 5.6659726562500001, 5.4098457031249998], [3.5233041992187499, 3.3359489746093751, 3.2895532226562501, 3.1626972656249999, 3.3691701660156248, 3.246654052734375, 3.2864155273437499, 3.1468691406249998, 3.28340380859375, 3.0963320312499998, 3.31488916015625], [3.6638259277343752, 3.8319042968749999, 3.765566162109375, 3.6108095703125, 3.7537172851562501, 3.62643408203125, 3.5064660644531251, 3.66663037109375, 3.7173835449218751, 3.6514638671875002, 3.779260009765625], [3.207746337890625, 3.2596235351562499, 3.2455019531249998, 3.0711311035156248, 3.1341501464843748, 3.1543505859374998, 3.1636875, 3.1325261230468748, 3.0776696777343751, 3.0813286132812499, 3.299830810546875], [3.4441669921875002, 3.5919899902343748, 3.398116943359375, 3.2619775390624999, 3.3315288085937498, 3.2573664550781252, 3.25912255859375, 3.4010576171875, 3.3321823730468751, 3.2188254394531248, 3.5285661621093749]]

reorder = [0,5,1,7,2,4,3,6]

data = []
for k in reorder:
    data.append(a_data[k])


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

print "\nDifference between experiment 1 and 2"
print "df = " + str(df(data[1],data[2]))
print "t = " + str(tstat(data[1],data[2]))

print "\nDifference between experiment 3 and 4"
print "df = " + str(df(data[3],data[4]))
print "t = " + str(tstat(data[3],data[4]))

print "\nDifference between experiment "
print "df = " + str(df(data[3],data[4]))
print "t = " + str(tstat(data[3],data[4]))

# generate a boxplot figure to compare the values
plt.boxplot(data, notch=False, sym='+', vert=False, whis=1.5)
plt.grid(True)
plt.axis([2.5, 7.5, 8.5, 0.5])
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



