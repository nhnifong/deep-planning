from __future__ import division
import pil
import glob
import os
import numpy

# create 100,000 patches of 32x32 each
total_patches = 100000
patch_org = (250,250)
patch_size = (32,32)

img_origin = "/media/Loonies/MFLICKR/"
patches_dest = "/media/Loonies/Patches/image/"

img_filenames = os.glob(img_origin + "*.png")
patches_per_image = total_patches // len(img_filenames) + 1
print "Extracting %i patches per image" % patches_per_image

patches_created = 0
patches = numpy.zeros(100000, 32**2, numpy.dtype.float16)

for n,src_image_name in enumerate(img_filenames):
    img = pil.open(src_image_name)
    x = randInt(0,img.width-1)
    y = randInt(0,img.height-1)
    patch_img = pil.greyscale(pil.resize(pil.crop(img,x,y,*patch_org),*patch_size))
    # save examples of patch images
    if n==0:
        pil.save(patch_img,"patch_example_%i_%i.png"%(n,i))
    flattened = numpy.array(map(lambda px: px/256, patch_img.pixels),dtype=numpy.float16)
    patches[patches_created] = flattened
    patches_created += 1
    if patches_created == total_patches:
        break

print "Patch extraction complete, begin whitening"

#perform whitening.
