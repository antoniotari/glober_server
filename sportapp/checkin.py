#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import json
import cgi
import cgitb
import base64
import random
import string
#import simplejson
from PIL import Image
from py4j.java_gateway import JavaGateway

#import the file with all the common constansts
from defs import *
from database import *
from follow import IAmFollow
from utility import ErrorLog,TimeUtc,RemovePassword,DateToLong
from wall import PostOnWall

CHECKIN_POST="just checked in"

def DoCheckin(useruid,businessid):
	dicti={}
	dicti['user_uid']=useruid
	dicti['business_id']=businessid
	insertedId=Insert('checkinlog',dicti)
        if insertedId==-1:
		dicti[KEY_RESULT]='cannot insert, data=%s'%json.dumps(dicti)
                dicti[KEY_ESIT]=ESIT_ERROR
        else:
                dicti[KEY_ESIT]=ESIT_OK
                dicti[KEY_RESULT]=insertedId
		#post the checkin on the wall	
		try:
			username=getValueS('user','username','uid',useruid)
			if username==None: username='a user'
			businessname=getValueS('business','name','idapi',businessid)
			if businessname==None: businessname=''
			address=getValueS('business','address','idapi',businessid)
			message="%s %s at %s  (%s)"%(username,CHECKIN_POST,businessname,address)
			PostOnWall(useruid,message,businessid,None,"%s"%insertedId)
		except Exception,e:
			ErrorLog("checkin file, dockeckin, error:%s"%e)
        return dicti
	
#------------------------------------------------------------
#------------------------
def ReturnCheckins(businessid,useruid):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT checkinlog.date,user.*,business.name as business_name FROM checkinlog,user,business WHERE user.uid=checkinlog.user_uid AND business.idapi=checkinlog.business_id AND business.idapi='%s';"%businessid
        dicti={}
	try:
                rowcount=cursor.execute(sql)
                results=cursor.fetchall()
                dicti[KEY_ESIT]=ESIT_OK
		resutA=[]
		for row in results:
                	if 'date' in row:
                        	row['datestring']="%s"%row['date']
				row['date']=TimeUtc(row['date'])
                                #del row['date']
                        #if 'registersince'in row: row['registersince']=TimeUtc(row['registersince'])# del row['registersince']
			#if 'password' in row: del row['password'] 
		#		row['date']="%s"%date
			#if 'lastonline' in row: row['lastonline']=TimeUtc(row['lastonline'])
			
			try:
				row['iamfollow']=IAmFollow(useruid,"%s"%row['uid'])
			except:
				row['iamfollow']=-1
			resutA.append(row)
                resutA=DateToLong(resutA)
                resutA=RemovePassword(resutA)
                #dicti=AddIsOnline(dicti)
		dicti[KEY_RESULT]=resutA
        except:
                dicti[KEY_ESIT]=ESIT_ERROR

        cursor.close()
        db.close()
        return dicti

	
