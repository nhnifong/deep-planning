# command used to capture audio
# sox -t mp3 "http://www.npr.org/streams/mp3/nprlive24.pls" npr.wav trim 0 2 channels 1 : newfile : restart
# produces numbered wav files 2 seconds in length,
# 1 channel, 16 bit signed PCM, 22100 samples per second.
from __future__ import division
import subprocess
import os
import sys
import time

while True:

    specpath = sys.argv[2]
    indir = sys.argv[1]
    wavfiles = os.listdir(indir)
    print "process %i wav files" % (len(wavfiles))
    
    for i,wf in enumerate(wavfiles):
        if not wf.endswith('wav'):
            continue
        inname = os.path.join(indir, wf)
        if not os.path.getsize(inname)==88444:
            continue
        inname = os.path.join(indir, wf)
        outname = os.path.join(specpath,wf.split('.')[0]+".png")
        subprocess.call(['sndfile-spectrogram',
                         '--no-border',
                         inname,
                         '1000',
                         '1000',
                         outname])
        os.remove(inname)
        print "created %s, %0.2f%% complete" % (outname, (i/len(wavfiles)*100))
    time.sleep(10)
