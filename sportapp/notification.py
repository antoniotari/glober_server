#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
from defs import *
from database import *
from utility import *

#-------------------------------------------------------------------------
#--------------
def InsertNotification(message,typeS,clickid,sender,receiver):
	delH={}
        delH['text']=message
        delH['type']=typeS
        delH['clickid']=clickid
	delH['sender_uid']=sender
	delH['receiver_uid']=receiver
        delH[KEY_RESULT]=Insert('notificationlog',delH)
        delH[KEY_ESIT]=ESIT_OK
        return delH

#-------------------------------------------------------------------------
#--------------
def ViewNotification(notifId):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="UPDATE notificationlog SET dateview=now() where id='%s'"%notifId
    	delH={}
	try:
                cursor.execute(sql)
                db.commit()
		delH[KEY_ESIT]=ESIT_OK
        except:
                db.rollback()
		delH[KEY_ESIT]=ESIT_ERROR
        cursor.close()
        db.close()
	return delH


#-------------------------------------------------------------------------
#--------------
def GetNotificationCount(userid):
	if userid=='undefined' or userid==None or userid=="None":return -1
	sql="SELECT count(*) as total FROM notificationlog WHERE receiver_uid='%s' AND dateview is NULL"%userid
	results=SelectS(sql)
        return results[0]['total']

#-------------------------------------------------------------------------
#--------------
def GetNotifications(userid):
	sql="SELECT notificationlog.*,notificationlog.sender_uid as user_uid,user.username,user.firstname,user.lastname  FROM notificationlog,user WHERE receiver_uid='%s' AND dateview is NULL AND user.uid=sender_uid"%userid
	delH={}
	delH[KEY_RESULT]=SelectS(sql)
        delH[KEY_ESIT]=ESIT_OK
        return delH
