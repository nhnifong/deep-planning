from __future__ import division
import Image
import glob
import os
import sys
import numpy
from random import randint

# create 100,000 patches of 32x32 each
total_patches = 100000
patch_org = (250,250)
patch_size = (32,32)

img_origin = sys.argv[1]
patches_dest = sys.argv[2]
outfile = sys.argv[3]

img_filenames = os.listdir(img_origin)
patches_per_image = total_patches // len(img_filenames) + 1
print "Extracting %i patches per image" % patches_per_image

patches_created = 0
patches = numpy.zeros((total_patches,patch_size[0]*patch_size[1]),
                      numpy.float32)
sav = 0

for n,src_image_name in enumerate(img_filenames):
    img = Image.open(os.path.join(img_origin,src_image_name))
    print src_image_name
    x = randint(0,img.size[0]-1-patch_size[0])
    y = randint(0,img.size[1]-1-patch_size[1])
    patch_img = img.crop((x,y,(x+patch_size[0]),(y+patch_size[1])))
    patch_img = patch_img.resize(patch_size).convert("L")
    # save examples of patch images
    if sav < 100:
        destname = os.path.join(patches_dest,"patch_example_%i.png"%sav)
        print "saving %s" % destname
        patch_img.save(destname)
        sav += 1
    flattened = numpy.array(map(lambda px: px/256, patch_img.getdata()),dtype=numpy.float32)
    patches[patches_created] = flattened
    patches_created += 1
    if patches_created == total_patches:
        break

print "Patch extraction complete"
print "saving %s" % outfile
numpy.save(outfile,patches)

#perform whitening.
