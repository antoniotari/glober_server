#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
#import the file with all the common constansts
from defs import *
from utility import ErrorLog,id_generator,DateToLong,strize
from database import Insert,SelectS,getValueS,existsS,QueryS
import pictures
from py4j.java_gateway import JavaGateway
import user

def updateframe():
	users=SelectS("SELECT uid FROM user")
	for row in users:
		uid=row['uid']
		img64=user.UserImage("%s"%uid,False)
		if img64[KEY_ESIT]==0 :
			CreateFrame(img64[KEY_RESULT]['picture64'],uid)
#----------------------------------------------------------------------------------------------
#----------
def CreateFrame(img64,userid):
	framebase="/media/hd2/sportapp/img/profilepic/frame/"	
	picbase="/media/hd2/sportapp/img/profilepic/"
	#save the image on disc
	filename="%s.png"%id_generator()
	pictures.CropResizeImg64Save(img64,120,120,"%s%s"%(picbase,filename))
	gateway = JavaGateway()
	gateway.entry_point.CreateFrame("%s%s"%(picbase,filename),"%s%s"%(framebase,filename))
	QueryS("UPDATE user SET marker='%s' WHERE uid='%s'"%("http://162.216.4.195/sex/img/profilepic/frame/%s"%(filename),userid))

#----------------------------------------------------------------------------------------------
#----------get any picture
def GetAnyPicture(picid,thumb):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql=''
        key=''
        if thumb==None:thumb='false'
        if thumb=='false':
        	key='picture64'
		sql="SELECT %s FROM userimages where id='%s' AND visible=1;"%(key,picid)
        else:
                key='thumb64'
                sql="SELECT %s FROM userimages where id='%s' AND visible=1;"%(key,picid)
        encodedimg=''
        try:
        	rowcount=cursor.execute(sql)
                results=cursor.fetchall()
                dicti={}
                dicti=results[0]
                encodedimg=dicti[key]
		#check if is a news picture
		if thumb=='false':
			if existsS('wall','userimages_id',picid):
				if getValueS('wall','newsid','userimages_id',picid)!=0:
					encodedimg=pictures.BlendEspnLogo(encodedimg)
	except Exception,e:
		ErrorLog("images file,GetAnyPicture , error:%s"%e)
                encodedimg= ''
        finally:
                cursor.close()
                db.close()
		return encodedimg

#----------------------------------------------------------------------------------------------
#----------
def GetProfilePicId(useruid):
	useruid=strize(useruid)
	try:
		retA= SelectS("SELECT id from userimages WHERE user_uid=%s and phototype=%d ORDER BY userimages.date DESC"%(useruid,PHOTOTYPE_PROFILE))
		if len(retA)==0:return -1
		return retA[0]['id']
	except Exception,e:
		ErrorLog("images file,GetProfilePicId , error:%s"%e)
		return -1



#----------------------------------------------------------------------------------------------
#----------
def GetAlbum(useruid,phototype):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT id,date FROM userimages where phototype='%s' and user_uid='%s' AND visible=1;"%(phototype,useruid)
        dicty={}
        try:
        	rowcount=cursor.execute(sql)
                results=cursor.fetchall()
                results=DateToLong(results)
                dicty[KEY_RESULT]=results
                dicty[KEY_ESIT]=ESIT_OK
	except Exception,e:
                ErrorLog("images file,GetAlbum , error:%s"%e)
                dicty[KEY_ESIT]=ESIT_ERROR
        cursor.close()
        db.close()
	return dicty


#----------------------------------------------------------------------------------------------
#----------
def CopyPicture(pictureid,typeToMoveTo):
	pictureid=strize(pictureid)
	returnJ={}
	mapIns=SelectS("SELECT user_uid,picture64,thumb64 from userimages WHERE id=%s"%pictureid)[0]
	mapIns['phototype']=strize(typeToMoveTo)
	result=Insert('userimages',mapIns)
	if result==-1:
		returnJ[KEY_ESIT]=ESIT_ERROR
	else:		
		returnJ[KEY_RESULT]=result#QueryS(("UPDATE userimages SET phototype=2,userimages.date=now() WHERE id="+pictureid)
        	returnJ[KEY_ESIT]=ESIT_OK
	return returnJ

#----------------------------------------------------------------------------------------------
#----------
def SetPicAsProfile(pictureid):
	return CopyPicture(pictureid,PHOTOTYPE_PROFILE)

#----------------------------------------------------------------------------------------------
#----------
def SetPicAsCover(pictureid):
        return CopyPicture(pictureid,PHOTOTYPE_COVER)

#----------------------------------------------------------------------------------------------
#----------
def DeletePicture(picid):
        #delH={}
        #delH['id']=postid
        #delH[KEY_RESULT]=Delete('userimages',delH)
        #delH[KEY_ESIT]=ESIT_OK
        return QueryS("UPDATE userimages SET visible=0 where id="+picid)

