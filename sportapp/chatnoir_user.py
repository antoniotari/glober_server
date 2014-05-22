#!/usr/bin/python
# -*- coding: utf-8 -*-
import cgi
import cgitb
import database
import utility
from defs import *
import json
#import emailsend
import pictures
import urllib2
import base64
import random
import string
from utility import ErrorLog

form=cgi.FieldStorage()
cmd="%s" % form.getvalue('cmd')

#----------------------------------------------------------------------------------------------
#----------
def UploadImage():
	image64="%s"%form.getvalue('image64')
	thumb=None
	mapRet={}
        try:
#		full=pictures.ResizeImg64(urllib2.unquote(image64.decode('utf8')))
                thumb=pictures.CropResizeImg64(urllib2.unquote(image64.decode('utf8')),44,44)
        except Exception,exc:
                ErrorLog("CHATNOIR UploadImage : %s"%exc)
        mapRet['esit']=2
	try:
		if thumb!=None:
			mapRet['esit']=0
        		mapRet['result']= database.QueryS("UPDATE chatnoir.user SET profilethumb='%s' WHERE qb_id=%s"%(thumb,"%s"%form.getvalue('qb_id'))) 
	except Exception,exc2:
                ErrorLog("CHATNOIR UploadImage exception 2: %s"%exc2)
	print json.dumps(mapRet)

#----------------------------------------------------------------------------------------------
#----------
def UpdateLocation():
	mapI={}
        latitude=form.getvalue('latitude')
        longitude=form.getvalue('longitude')
        qb_id=form.getvalue('qb_id')
        if latitude==None or longitude==None:return
	database.QueryS("UPDATE chatnoir.user SET latitude=%s , longitude=%s WHERE qb_id=%s"%(latitude,longitude,qb_id))
	#print "UPDATE chatnoir.user SET latitude=%s , longitude=%s WHERE qb_id=%s"%(latitude,longitude,qb_id)
	mapI[KEY_ESIT]=ESIT_OK
	GetUsers()

#----------------------------------------------------------------------------------------------
#----------
def UpdateLanguage():
        mapI={}
        language=form.getvalue('language')
        qb_id=form.getvalue('qb_id')
        database.QueryS("UPDATE chatnoir.user SET language='%s'  WHERE qb_id=%s"%(language,qb_id))
        #print "UPDATE chatnoir.user SET latitude=%s , longitude=%s WHERE qb_id=%s"%(latitude,longitude,qb_id)
        mapI[KEY_ESIT]=ESIT_OK
        GetUsers()

#----------------------------------------------------------------------------------------------
#----------
def GetUsers():
	dicty={}
        try:
                mapI={}
                latitude=form.getvalue('latitude')
                longitude=form.getvalue('longitude')
		maxpeople='300'#form.getvalue('')
                qb_id=form.getvalue('qb_id')
                language=database.getValueS('chatnoir.user','language','qb_id',qb_id)
		if latitude==None or longitude==None:
                        longitude=database.getValueS('chatnoir.user','longitude','qb_id',qb_id)
                        latitude=database.getValueS('chatnoir.user','latitude','qb_id',qb_id)
		queryPeople="SELECT chatnoir.user.*,( 3959 * acos( cos( radians(%s) ) * cos( radians( chatnoir.user.latitude ) ) * cos( radians( chatnoir.user.longitude ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( chatnoir.user.latitude ) ) ) ) AS distance FROM  chatnoir.user WHERE chatnoir.user.showlocation=1 AND (chatnoir.user.language='%s' OR chatnoir.user.language='all')  AND (chatnoir.user.latitude!=-1 OR chatnoir.user.longitude!=-1) AND chatnoir.user.qb_id != %s GROUP BY chatnoir.user.qb_id Order By distance limit %s"%(latitude,longitude,latitude,language,qb_id,maxpeople)
                #dicty['query']=queryPeople
		dicty[KEY_ESIT]=ESIT_OK
                dicty[KEY_RESULT]= database.SelectS(queryPeople)
        except Exception , d:
                dicty[KEY_ESIT]=ESIT_ERROR
                dicty['error']="%s"%d
                utility.ErrorLog("chatnoir_user.py  %s"%d)
        print json.dumps(dicty)

def UserInfo():
	dicty={}
        try:
                email="%s" % form.getvalue('email')
		mapI={}
                mapI['latitude']=form.getvalue('latitude')
                mapI['longitude']=form.getvalue('longitude')
		mapI['username']=form.getvalue('username')
		mapI['qb_id']=form.getvalue('qb_id')
		if(database.existsS('chatnoir.user','qb_id',mapI['qb_id'])):
			dicty[KEY_ESIT]=1
			dicty[KEY_RESULT]=database.getValueS('chatnoir.user','id','qb_id',mapI['qb_id']) 
			database.QueryS("UPDATE chatnoir.user SET latitude=%s , longitude=%s , username='%s' WHERE qb_id=%s"%(mapI['latitude'],mapI['longitude'],mapI['username'],mapI['qb_id']))
		else:
			dicty[KEY_ESIT]=ESIT_OK
			dicty[KEY_RESULT]= database.Insert('chatnoir.user',mapI)
        except Exception , d:
                dicty[KEY_ESIT]=ESIT_ERROR
		dicty['error']="%s"%d
		utility.ErrorLog("chatnoir_user.py  %s"%d)
	print json.dumps(dicty)

if __name__=="__main__":
        print "Content-type:application/json\r\n\r\n"
	#ErrorLog("%s"%cmd)
	if cmd=='userinfo':UserInfo()
	elif cmd=='getusers':GetUsers()
	elif cmd=='updatelocation':UpdateLocation()
	elif cmd=='uploadimage':UploadImage()
	elif cmd=='updatelanguage':UpdateLanguage()	
