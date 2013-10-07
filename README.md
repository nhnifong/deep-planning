deep-planning
=============

##### An application of stacked denoising autoencoders to multi-modal (images and audio) abstract feature discovery

#### Abstract
One of the most impressive qualities of the brain is its neuro-plasticity. The neocortex has roughly the same structure throughout its whole surface, yet it is involved in a variety of different tasks from vision to motor control, and regions which once performed one task can learn to perform another. Machine learning algorithms which aim to be plausible models of the neocortex should also display this plasticity. One such candidate is the stacked denoising autoencoder (SDA). SDA's have shown promising results in the field of machine perception where they have been used to learn abstract features from unlabeled data. In this thesis I develop a flexible distributed implementation of an SDA and train it on images and audio spectrograms to experimentally determine properties comparable to neuro-plasticity, Specifically, I compare the visual-auditory generalization between a multi-level denoising autoencoder trained with greedy, layer-wise pre-training (GLWPT), to one trained without. I test a hypothesis that networks pre-trained on one sensory modality will perform better on the other modality than randomly initialized networks trained for an equal total number of epochs. Furthermore, I also test the hypothesis that the magnitude of improvement gained from this pre-training is greater when GLWPT is applied than when it is not.



#### Dependencies
python 2.6 or 2.7
Theano 
numpy
matplotlib
PIL (Python Imaging Library)

#### Overview

plas.py runs the main experiment. The locations of the datasets are hardcoded in plas.py to external drives on my development machine. Those datasets can be produced from the MFLICKR-1M dataset and collected wav files using imageprep.py and audioprep.py respectively.
