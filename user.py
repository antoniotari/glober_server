#!/usr/bin/python
import MySQLdb
import json
import base64
import random
import string
#import the file with all the common constansts
from defs import *
from database import *


def DismissFtDialogChat(userid,sender,message,newmessage):
	exD={}	
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="UPDATE `ChatLog` SET Message='%s' WHERE FromUser='%s' AND ToUSer='%s' AND Message='%s';"%(newmessage,sender,userid,message)
	try:
                queryEsit=cursor.execute(sql)
                db.commit()
		exD[KEY_ESIT]=0
        except:
                db.rollback()
		exD[KEY_ESIT]=2
                
        cursor.close()
        db.close()
	return exD;


def GetFacetime(userid,deviceid):
	exD={}
        #exD['device_id']=deviceid
        exD['user_id']=userid
	ft=getValueTime('devicemode','facetime_contact',exD)
	esit=0
	if ft==None:esit=2
	if ft=='':esit=2
	exD[KEY_ESIT]=esit
	exD[KEY_RESULT]=ft
	return exD

def CheckFacetime(userid,deviceid):
	exD={}
        #exD['device_id']=deviceid
        exD['user_id']=userid
	ft=getValueTime('devicemode','facetime_contact',exD)
        esit=True
        if ft==None:esit=False
        if ft=='':esit=False
	return esit

#----------------------------------------------------------------------------------------------
#----------get the value from the table where key=value
def getValueTime(table,keyToGet,hashMap):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)

        whereStat=' WHERE '
        for key, value in hashMap.iteritems():
                whereStat=whereStat+key+"='"+value+"' AND "
        sql="SELECT "+keyToGet+" FROM "+table+whereStat[:-5]+" ORDER BY register_date DESC;"
        #sql="SELECT "+keyToGet+" FROM "+table+" WHERE "+key+"='"+value+"';"
        valueToGet=''
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                dicti=results[0]
                valueToGet=dicti[keyToGet]
        except:
                valueToGet=''
        cursor.close()
        db.close()
        return valueToGet


def UpdateDeviceInfo(userid,token,development,devicetype,deviceid,deviceversion,faceContact):
	resultJ={}
	try:
		table='devicemode'
		exD={}
		exD['device_id']=deviceid
		exD['user_id']=userid
		if exists(table,exD):
			resultJ[KEY_ESIT]=1
			CheckAndUpdate(token,'device_token',exD) 
			CheckAndUpdate(development,'development',exD)	
               	 	CheckAndUpdate(devicetype,'device_type',exD)              
                	CheckAndUpdate(deviceversion,'version',exD)              
                	CheckAndUpdate(faceContact,'facetime_contact',exD)              	
		else:
			resultJ[KEY_ESIT]=0
			if development!=None: exD['development']=development
			if token!=None:exD['device_token']=token
			if devicetype!=None:exD['device_type']=devicetype
			if deviceversion!=None:exD['version']=deviceversion
			if faceContact!=None:exD['facetime_contact']=faceContact
			Insert('devicemode',exD)
		resultJ['validfacetime']=CheckFacetime(userid,deviceid)
	except Exception ,d:
		resultJ[KEY_ESIT]=2
		resultJ['error']="%s"%d
	return resultJ
	

def CheckAndUpdate(newValue,keyToUpdate,hashCond):
	if newValue==None:return
	if newValue=='':return
	if newValue=='0':return
	table='devicemode'
	oldValue=getValue(table,keyToUpdate,hashCond)
	if oldValue != newValue:
		db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
		#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
                cursor=db.cursor(MySQLdb.cursors.DictCursor)
		whereStat=' WHERE '
        	for key, value in hashCond.iteritems():
                	whereStat=whereStat+key+"='"+value+"' AND "
		sql="UPDATE devicemode SET %s='%s' %s"%(keyToUpdate,newValue,whereStat[:-5])
		try:
                	queryEsit=cursor.execute(sql)
                	db.commit()
        	except:
                	db.rollback()
		cursor.close()
		db.close()

