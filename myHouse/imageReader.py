import argparse
import logging
import tempfile
import os, sys

import cv2.cv as cv
import tesseract

import math

from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL import ImageChops

# sudo apt-get install libcv2.3 libcvaux2.3 libhighgui2.3 python-opencv opencv-doc libcv-dev libcvaux-dev libhighgui-dev
# sudo apt-get install tesseract-ocr

##
# Crop borders off an image.
#
# @param im Source image.
# @param bgcolor Background color, using either a color tuple or
# a color name (1.1.4 only).
# @return An image without borders, or None if there's no actual
# content in the image.
def autocrop(im, bgcolor):
    bbox = None
    if im.mode != "RGB":
        im = im.convert("RGB")
        
    bg = Image.new("RGB", im.size, bgcolor)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    
    return None # no contents

def denoise(im):
    im = im.filter(ImageFilter.SMOOTH)
    im = im.filter(ImageFilter.SMOOTH)
    im = im.filter(ImageFilter.SMOOTH)
    
    # 
    enh = ImageEnhance.Contrast(im)
    im = enh.enhance(1.6)
        
        
    source = im.split()
    R, G, B = 0, 1, 2
    
    def fcn(val):
        pi2 = (math.pi/2)
        
        r = math.sin( pi2*math.sin( pi2 *(float(val)*0.85/256) ) ) 
        
        #r = 0 if r<128 else 256
        
        m1 = 0.8
        m2 = 1.1
        r = (m1*r) if r<0.5 else (m2*r)
        
        return int(256*r)

    out =   source[R].point(fcn)
    
    source[R].paste(out, None)
    source[G].paste(out, None)
    source[B].paste(out, None)

    im = Image.merge(im.mode, source)
    return im


class ImageReader:
    def __init__(self, file, args):
        self.file = file
        self.args = args
        self.result = None
        self.tempFile = None
    
    def init(self):
        (__, self.tempFile) = tempfile.mkstemp(".png")
        self.load()
    
    def destroy(self):
        os.unlink(self.tempFile)
    
    def load(self):
        im = Image.open(self.file)
        
        # turn it grayscale
        enh = ImageEnhance.Color(im)
        im = enh.enhance(0)

        # autocrop the image        
        im = autocrop(im, im.getpixel((im.size[0]-1, im.size[1]-1)))
        
        # resize the image to 400px wide
        r = float(im.size[1]) / im.size[0]
        m = 400
        w = int(m)
        h = int(m * r)
        im = im.resize((w, h ))

        # custom denoiser function
        im = denoise(im)
        
        # 
        #enh = ImageEnhance.Sharpness(im)
        #im = enh.enhance(10.5)
        
        im.save(self.tempFile)

        return self
        
    def detect(self):
        api = tesseract.TessBaseAPI()
        api.Init(".","eng",tesseract.OEM_DEFAULT)
        api.SetVariable("tessedit_char_whitelist", "0123456789 ")
        api.SetPageSegMode(tesseract.PSM_AUTO)

        mBuffer=open(self.tempFile,"rb").read()
        self.result = tesseract.ProcessPagesBuffer(mBuffer, len(mBuffer), api)
        
        return self
    
    def displayInput(self):
        """
        try:
            img = cv.LoadImage(self.file)
            cv.NamedWindow("Input", cv.CV_WINDOW_AUTOSIZE )
            cv.ShowImage("Input", img )
            cv.WaitKey(15000)
            cv.DestroyWindow("Input")
        except:
            Image.open(self.file).show()
        #return None
        """
        Image.open(self.file).show()

    def displayOutput(self):
        Image.open(self.tempFile).show()
            

    
    def get(self):
        return self.result



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter gatherer results.')
    parser.add_argument('-file',            dest='file',            action='store',     type=str,   default=[],       help='TODO')
    parser.add_argument('--displayInput',   dest='displayInput',    action='store',     type=bool,  default=False,    help='TODO')
    parser.add_argument('--displayOutput',  dest='displayOutput',   action='store',     type=bool,  default=False,    help='TODO')
    args = parser.parse_args()
    
    logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

    reader = ImageReader(args.file, args)
    
    reader.init()
    print reader.detect().get()
    
    if args.displayInput:
        reader.displayInput()
        
    if args.displayOutput:
        reader.displayOutput()
    
    reader.destroy()
