#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import json
import cgi
import cgitb
import base64
import random
import string
import urllib2
import urllib
#import simplejson
from PIL import Image

#import the file with all the common constansts
from database import SelectS,QueryS,existsS
from defs import *
from user import *
import ErrorLog
#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
#-----CONSTANTS
#HOST=           'localhost'
#DBUSER=         'antonio'
#DBPASS=         'glorious.and.free'
#DBNAME=         'glober'

#KEY_ESIT=       'esit'
#KEY_RESULT=     'result'
#KEY_CMD=        'cmd'

#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")

#BASE_URL=		"http://162.216.4.195"
#CHAT_IMAGE_KEY=		"afsjktirntly845kfhtk594jrtjh49lrtj4955555555klrktlrjkkjhhjkhgjh"
#UPLOAD_IMAGE_URL=	"http://162.216.4.195/love/img/profilepic/images/"
#BASE_PICTURE_DIR=	"/media/hd2/glober/img/profilepic/"
#UPLOAD_IMAGE_DIR=	"images/"
#UPLOAD_THUMB_DIR=	"images/thumb/"

#CMD_SENDPICTOUSR=	"sendpictousr"

#THUMB_PIC_W = 120 # this is the maximum width of the images
#THUMB_PIC_H = 120 # this is the maximum height of the images
#ratio = 1. * THUMB_PIC_W / THUMB_PIC_H

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
#-----BEGIN of the Api class
class Api:
        'api to access read write into the database'
        countI=0

        #--------------------------------------------------------------------
        #-----constructor
        def __init__(self):
                self.countI=self.countI+1

        #--------------------------------------------------------------------                   
        #-----destructor
        def __del__(self):
                try:
                        self.DBclose()
                        self.countI-=1
                except:
                        print ''

        #--------------------------------------------------------------------
        #-----
        def DB(self):
                #if db.open==0:
                #       db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
                return db

        #--------------------------------------------------------------------
        #-----  
	def DBclose(self):
                try:
                        if db.open:
                                db.close()
                except:
                        print ''
	
	#--------------------------------------------------------------------
        #-----it generates a random string, useful for filenames
	def id_generator(self,size=22, chars=string.ascii_uppercase + string.digits):
    		return ''.join(random.choice(chars) for x in range(size))

        #--------------------------------------------------------------------
        #-----run the appropriate function for the received command
        def HandleCommand(self):
                form=cgi.FieldStorage()
                cmd="%s" % form.getvalue(KEY_CMD)
                if cmd=='test':
                        print self.TestConnection(form)
                elif cmd=='test1':
                        print 'test1'
                elif cmd==CMD_SENDPICTOUSR:
			print self.SendPicToUsr(form)
		elif cmd=="updatedeviceinfo":
			dicti=UpdateDeviceInfo(form.getvalue('uid'),form.getvalue('token'),form.getvalue('development'),form.getvalue('devicetype'),form.getvalue('deviceid'),form.getvalue('deviceversion'),form.getvalue('facetime'))
			print json.dumps(dicti)
		elif cmd=='getfacetime':
			#print 'helo'+form.getvalue('uid')+form.getvalue('deviceid')
			dicti=GetFacetime(form.getvalue('uid'),form.getvalue('deviceid'))	
			print json.dumps(dicti)
		elif cmd=='updatechatbyid':
                        print json.dumps(DismissFtDialogChat(form.getvalue('userid'),form.getvalue('sender'),form.getvalue('message'),form.getvalue('newmessage')))
		elif cmd=='updatechatftdialog':
			print json.dumps(DismissFtDialogChat(form.getvalue('chatid'),form.getvalue('message')))
		elif cmd=="getqbid":
			if existsS('quickblox','user_userid',form.getvalue('userid')): 
				print "{\"value\":%s}"%SelectS("SELECT quickblox_uid FROM quickblox WHERE user_userid='%s'"%form.getvalue('userid'))[0]['quickblox_uid']
			else: 
				print "{\"value\":-1}"
		elif cmd=="setqbid":	
			print "%s"%QueryS("INSERT INTO quickblox (quickblox_uid,user_userid)VALUES('%s','%s')"%(form.getvalue('bloxid'),form.getvalue('userid')))
		elif cmd==CMD_REGISTERDEVICE:
			print 'cazzone'
			#print self.RegisterToken(form)
		elif cmd=='deletechats':
			print "%s"%QueryS("UPDATE ChatLog SET visible=0 where FromUser='%s' OR ToUSer='%s'"%(form.getvalue('userid'),form.getvalue('userid')))
		elif cmd=='setpurchase':
			print "%s"%QueryS("INSERT INTO purchase (itunesid,user_uid)VALUES('%s','%s')"%(form.getvalue('itunesid'),form.getvalue('userid')))
		elif cmd=="getpurchase":
                        if existsS('purchase','user_uid',form.getvalue('userid')):
                                print "{\"value\":%s}"%json.dumps(SelectS("SELECT * FROM purchase WHERE user_uid='%s' order by datepurchased desc"%form.getvalue('userid'))[0])
                        else:
                                print "{\"value\":-1}"
		else:
                        print 'error command unknown'

	def ErrorLog(self,message,typeS):
		d=urllib2.urlopen("http://162.216.4.195:8080/Glober3/api?cmd=errorlog&error=%s&message=%s"%(urllib.quote(message),urllib.quote(typeS))).read()
  		#o = xmltodict.parse(d)

        #--------------------------------------------------------------------
        #-----
        def TestConnection(self,form):
                cursor=self.DB().cursor(MySQLdb.cursors.DictCursor)
                sql="SELECT * FROM user;"
                try:
                        cursor.execute(sql)
                        result = self.RetJson(cursor)
                        dd={}
                        dd[KEY_ESIT]=0
                        dd[KEY_CMD]=cmd="%s" % form.getvalue(KEY_CMD)
                        dd[KEY_RESULT]=result
                        return json.dumps(dd)
                except Exception ,df:
			ErrorLog.ErrorLog("%s"%df,"test_python")
                        return "exception"
                finally:
                        cursor.close()

	#--------------------------------------------------------------------
        #-----  
        def RegisterToken(self,form):
                responseJ={}
                responseJ[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
                tokenS=form.getvalue("token")
                typeS=form.getvalue("type")
                deviceId=form.getvalue("deviceid")
                userUid=form.getvalue("useruid")
                development=""+form.getvalue("development")
                version=form.getvalue("version")
                cursor=self.DB().cursor(MySQLdb.cursors.DictCursor)
                sql="INSERT INTO device (development,devicetype,deviceid,devicetoken,user_uid,version) VALUES ('%s','%s','%s','%s','%s','%s');"%(development,typeS,deviceId,tokenS,userUid,version)
           
		try:
                        cursor.execute(sql)
                        db.commit()
                        responseJ[KEY_ESIT]=0
                except:
                        db.rollback()
                        responseJ[KEY_ESIT]=2
                finally:
                        cursor.close()

                return json.dumps(responseJ)

	#--------------------------------------------------------------------
        #-----	
	def SendPicToUsr(self,form):
		responseJ={}
		imgData=form.getvalue("image")
		chatId=form.getvalue("chat_id")
		filename=self.id_generator()+chatId+".png" #RandomString(chatId);
		
		#update the chat
		cursor=self.DB().cursor(MySQLdb.cursors.DictCursor)
        	sql="UPDATE ChatLog SET Message='"+CHAT_IMAGE_KEY+UPLOAD_IMAGE_URL+filename+"' WHERE ChatLogID="+chatId+" AND Message='afsjktirntly845kfhtk594jrtjh49lrtj4955555555klrktlrjkkjhhjkhgjhcom.antoniotari.glober.waiting_image';"
		#self.ErrorLog("%s"%(sql),"SendPicToUsr_python")
		try:
        		intres=cursor.execute(sql)
        		db.commit()
        	#	self.ErrorLog("%s response:%s"%(sql,intres),"SendPicToUsr_python")
			if intres>0:
				responseJ["chat"]="true"
			else:
				responseJ["chat"]="false"
        	except Exception,d:
        		db.rollback()
			ErrorLog.ErrorLog("%s"%d,"SendPicToUsr_python")
        		responseJ["chat"]="false"
        	finally:
            		cursor.close()
		
		imageDest=BASE_PICTURE_DIR+UPLOAD_IMAGE_DIR+filename
		responseJ["filename"]=UPLOAD_IMAGE_URL+filename;
		
		fh = open(imageDest, "wb")
		fh.write(imgData.decode('base64'))
		fh.close()
	
		#save the thumbnail
		self.CropResizeImg(imageDest,BASE_PICTURE_DIR+UPLOAD_THUMB_DIR+filename,THUMB_PIC_W,THUMB_PIC_H);		

		dd={}
		dd[KEY_ESIT]=0
                dd[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
                dd[KEY_RESULT]=responseJ
		return json.dumps(dd)	
       
	#--------------------------------------------------------------------
        #-----crops and resuzes the image to create the thumbnail 
	def CropResizeImg(self,origFilePath,destFilePath,img_w,img_h):
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

	#--------------------------------------------------------------------
        #-----returns the json string from the fetched array
        def RetJson(self,cursor):
                results=cursor.fetchall()
                desc=cursor.description
                i=0
                resultA=[]
                for row in results:
                        d={}
                        i=0
                        for row2 in row:
                                d[row2]="%s"%(row[row2])
                                i=i+1
                        resultA.append(d)
                return resultA

#-----END of the Api class              
#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def main():
        print "Content-type:application/json\r\n\r\n"
        try:
                api=Api()
                with api.DB():
                        api.HandleCommand()
                api.DBclose()
                del api
        except:
                de={}
                de[KEY_ESIT]=-1
                de[KEY_RESULT]='error main() exception'
                print json.dumps(de)

        if db.open:
                print 'databse not closes!'


#----------------------------------------------------------------------------
#-----START the script

if __name__ == '__main__':
    main()

#----------------------------------------------------------------------------

                             
