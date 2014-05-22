#!/usr/bin/python
#from io import StringIO
from StringIO import StringIO
import base64
#from base64 import decodestring
import random
import string
from utility import ErrorLog,id_generator
from PIL import Image 
import urllib
import urllib2
import json

DEFAULTNOIMAGE_PATH=    "/media/hd2/sportapp/defaultthumb.png"

#--------------------------------------------------------------------
#-----
def Base64FromUrl(url):
	return base64.b64encode(urllib.urlopen(url).read())	

#--------------------------------------------------------------------
#-----crops and resuzes the image to create the thumbnail 
def CropResizeImg(origFilePath,destFilePath,img_w,img_h):
	ratio = 1. * img_w /img_h
        im = Image.open(origFilePath) # open the input file
        (width, height) = im.size        # get the size of the input image

        if width > height * ratio:
        	# crop the image on the left and right side
                newwidth = int(height * ratio)
                left = width / 2 - newwidth / 2
                right = left + newwidth
                # keep the height of the image
                top = 0
                bottom = height
	elif width < height * ratio:
        	# crop the image on the top and bottom
                newheight = int(width * ratio)
                top = height / 2 - newheight / 2
                bottom = top + newheight
                # keep the width of the impage
                left = 0
                right = width
	if width != height * ratio:
                im = im.crop((left, top, right, bottom))

        im = im.resize((img_w,img_h),Image.BICUBIC) #ANTIALIAS,BICUBIC,BILINEAR,NEAREST 
        #im.save(fout, "jpeg", quality = 100) # save the image
        #fout.close()
        im.save(destFilePath)


def CropResizeImg64Save(orig64,img_w,img_h,dest):
	dest64=CropResizeImg64(orig64,img_w,img_h)
	im=Image.open(StringIO(base64.b64decode(dest64)))
	im.save(dest)

def CropResizeImg64(orig64,img_w,img_h):
	ratio = 1. * img_w /img_h
	#if isinstance(orig64, str):
        #	orig64 = StringIO(orig64)
	#im = Image.open(orig64)
	#image = Image.fromstring('RGB',(width,height),decodestring(orig64))
	#im = Image.open(StringIO(base64.b64decode(orig64))) # open the input file
	
	#image = open("/media/hd2/sportapp/imagetempthumb.png", "wb")
	#image.write(base64.b64decode(orig64))#.decode('base64'))
	#image.close()
	#im = Image.open("/media/hd2/sportapp/imagetempthumb.png")
	im=Image.open(StringIO(base64.b64decode(orig64)))
	(width, height) = im.size        # get the size of the input image
	#return "w:%d h:%d"%(width,height)
        if width > height * ratio:
                # crop the image on the left and right side
                newwidth = int(height * ratio)
                left = width / 2 - newwidth / 2
                right = left + newwidth
                # keep the height of the image
                top = 0
                bottom = height
        elif width < height * ratio:
                # crop the image on the top and bottom
                newheight = int(width * ratio)
                top = height / 2 - newheight / 2
                bottom = top + newheight
                # keep the width of the impage
                left = 0
                right = width
        if width != height * ratio:
                im = im.crop((left, top, right, bottom))

        im = im.resize((img_w,img_h),Image.BICUBIC) #ANTIALIAS,BICUBIC,BILINEAR,NEAREST 
	buf= StringIO()
	im.save(buf, format= 'PNG')
	jpeg= buf.getvalue()
	return base64.b64encode(jpeg)

	#savepath="/media/hd2/sportapp/pic_temp/%s.png"% id_generator(7)        
	#result64=''
	#try:
	#	im.save(savepath)
	#	with open(savepath, "rb") as image_file:
    	#		result64 = base64.b64encode(image_file.read())
	#	#im.save(fout, "jpeg", quality = 100) # save the image
        #	#fout.close()
	#except:
	#	with open(DEFAULTNOIMAGE_PATH, "rb") as image_file:
        #                result64 = base64.b64encode(image_file.read())
        #return result64


def ResizeImg64(orig64,basesize=900,qualityJpg=70):
        #ratio = 1. * img_w /img_h
        im=Image.open(StringIO(base64.b64decode(orig64)))
	(width, height) = im.size        # get the size of the input image
	if width<basesize:basesize=width
	
        im = im.resize((basesize,height/(width/basesize)),Image.BICUBIC) #ANTIALIAS,BICUBIC,BILINEAR,NEAREST

	#convert the image to RGB
        if im.mode != "RGB":
                im = im.convert("RGB")        

	buf= StringIO()
	try:
		im.save(buf, "JPEG", quality=qualityJpg, optimize=True, progressive=True)
        except Exception, d:
		try:
			ErrorLog("ResizeImg64 error, saving no optimization: %s"%d)
			im.save(buf, "JPEG", quality=qualityJpg-10)
		except Exception,dfg:
			try:
				ErrorLog("ResizeImg64 error, saving uncompressed: %s"%dfg)
				im.save(buf, format= 'JPEG')
			except Exception ,k:
				ErrorLog("ResizeImg64 INNER error,saving png: %s"%k)
				im.save(buf, format= 'PNG')
        jpeg= buf.getvalue()
        return base64.b64encode(jpeg)


def BlendEspnLogo(orig64):
	#orig64=JpgToPng64(orig64)
	im=Image.open(StringIO(base64.b64decode(orig64)))
	im2 = Image.open("/media/hd2/sportapp/powered-by-espn-silver_200.png")
	(width, height) = im.size
	basesize=width/7
	im2 = im2.resize((basesize,height/(width/basesize)),Image.BICUBIC)
	im.paste(im2,((width-basesize)-5,(height-(height/(width/basesize)))-5))
	buf= StringIO()
        try:
        	im.save(buf, format= 'JPEG')
        except Exception ,k:
        	ErrorLog("BlendEspnLogo error,saving png: %s"%k)
                im.save(buf, format= 'PNG')
        jpeg= buf.getvalue()
        return base64.b64encode(jpeg)


def JpgToPng64(orig64):
	im=Image.open(StringIO(base64.b64decode(orig64)))
	buf= StringIO()
        im.save(buf, format= 'PNG')
        jpeg= buf.getvalue()
        return base64.b64encode(jpeg)
