#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import json
import base64
import random
import string
from dateutil import parser
import datetime
import time
#import the file with all the common constansts
from defs import *
from database import *
from utility import *
from user import UploadImage
from images import GetAnyPicture
from pictures import CropResizeImg64,ResizeImg64
#-------------------------------------------------------------------------
#--------------get the number of unread chats, total
def GetUnread(userid):
	if userid==None : return -1
	try:
		db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
		#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        	cursor=db.cursor(MySQLdb.cursors.DictCursor)
        	sql="SELECT count(*) as total FROM chatlog WHERE user2="+userid+" AND dateview is NULL AND chatvisible=1"
        	rowcount=0
        	try:
                	queryEsit=cursor.execute(sql)
                	results=cursor.fetchall()
                	dicti=results[0]
                	rowcount=dicti['total']
        	except:
                	rowcount=-1
        	cursor.close()
        	db.close()
        	return rowcount
	except:
		return -1

#-------------------------------------------------------------------------
#--------------
def GetAllChats(userid):
	returnJ={}
	if userid=='undefined' or userid==None or userid=="None":
		returnJ[KEY_ESIT]=ESIT_ERROR
		return returnJ
	#ErrorLor(userid)		
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        #sql="SELECT user.username, user.uid, COUNT( * ) AS total FROM user, chatlog WHERE  `user2` =%s AND user1 = user.uid AND dateview IS NULL GROUP BY user1 UNION SELECT user.username, user.uid, 0 as total FROM user, chatlog WHERE  `user2` =%s AND user1 = user.uid AND dateview IS NOT NULL GROUP BY user1"%(userid,userid)
#        sql="SELECT user.username, chatlog.message, MAX(chatlog.datesend) AS datelast, user.uid, COUNT( * ) AS total FROM user, chatlog WHERE  `user2` =%s AND user1 = user.uid AND dateview IS NULL GROUP BY user1 UNION SELECT user.username, chatlog.message, MAX(chatlog.datesend) AS datelast, user.uid, 0 AS total FROM user, chatlog WHERE  `user2` =%s AND user1 = user.uid AND dateview IS NOT NULL GROUP BY user1"%(userid,userid)
	#sql="((SELECT user.username,user.firstname,user.lastname, ch.message, MAX( id ) AS lastid, MAX( ch.datesend ) AS datelast, user.uid, count(*) AS total FROM user, (SELECT * FROM chatlog WHERE user1 =  '%s' OR user2 =  '%s' ORDER BY chatlog.datesend DESC) AS ch WHERE ch.dateview IS NULL AND ((user2 = user.uid AND user2 !=  '%s')OR (user1 = user.uid AND user1 !=  '%s')))UNION (SELECT user.username,user.firstname,user.lastname, ch.message, MAX( id ) AS lastid, MAX( ch.datesend ) AS datelast, user.uid, 0 AS total FROM user, (SELECT * FROM chatlog WHERE user1 =  '%s' OR user2 =  '%s' ORDER BY chatlog.datesend DESC) AS ch WHERE ch.dateview IS NOT NULL AND ((user2 = user.uid AND user2 !=  '%s')OR (user1 = user.uid AND user1 !=  '%s'))))GROUP BY uid"%(userid,userid,userid,userid,userid,userid,userid,userid)
	sql="SELECT unichat.*,(count(uid)+min(subtr))*total1 as total FROM ((SELECT user.username, user.firstname, user.lastname, ch.message,( id ) AS lastid,( ch.datesend ) AS datelast,user.uid, 1 AS total1,0 as subtr,user2 as receiver FROM user, (SELECT * FROM chatlog WHERE (user1 =  '%s' OR user2 =  '%s') AND chatvisible=1 ORDER BY chatlog.datesend DESC) AS ch WHERE ch.dateview IS NULL AND ((user2 = user.uid AND user2 !=  '%s')OR (user1 = user.uid AND user1 !=  '%s')))UNION (SELECT user.username, user.firstname, user.lastname, ch.message, ( id ) AS lastid, ( ch.datesend ) AS datelast, user.uid, 0 AS total1,-1 as subt,user2 as receiver FROM user, (SELECT * FROM chatlog WHERE (user1 =  '%s' OR user2 =  '%s') AND chatvisible=1 ORDER BY chatlog.datesend DESC) AS ch WHERE ch.dateview IS NOT NULL AND ((user2 = user.uid AND user2 !=  '%s')OR (user1 = user.uid AND user1 !=  '%s')) GROUP BY user.uid)) AS unichat GROUP BY uid ORDER BY datelast DESC"%(userid,userid,userid,userid,userid,userid,userid,userid)
	try:
                queryEsit=cursor.execute(sql)
        	results=cursor.fetchall()
		resultA=[]
		for row in results:
			if 'subtr' in row : del row['subtr']
			if 'total1' in row : del row['total1']
			if 'receiver' in row:
				if row['receiver']==row['uid']:row['total']=0
				del row['receiver']
			if 'datelast' in row:
				if row['datelast']!=None:
					dlS="%s"%row['datelast']
					dl=parser.parse(dlS)
					dnow=datetime.datetime.now()
					dsub=dnow-dl
					row['passedtime']=time.mktime(dnow.timetuple())-time.mktime(dl.timetuple()) #dsub.seconds
					row['date_last']=time.mktime(dl.timetuple()) #%row['datelast']
				del row['datelast']

			if(row['message'].isdigit):
				mapE={}
				mapE['id']=row['lastid']
				mapE['type']='p'
				if exists('chatlog',mapE):	
					row['message']="sent you a picture"
			#if 'chattype' in row:
				#if row['chattype']=='p': 
				#	row['message']="sent you a picture"

			if row['username']!=None:
				resultA.append(row)
		returnJ[KEY_RESULT]=resultA
		returnJ[KEY_ESIT]=ESIT_OK
        except:
                returnJ[KEY_ESIT]=ESIT_ERROR
        cursor.close()
        db.close()
	return returnJ


#-------------------------------------------------------------------------
#--------------
def InsertChat(fromuser,touser,message,typeS,synctime):
	mapInsert={}
        mapInsert['user1']=fromuser
        mapInsert['user2']=touser
        mapInsert['type']=typeS
	if synctime!=None: mapInsert['synctime']=synctime
	if typeS==CHAT_TYPECHAT:
		mapInsert['message']=message
	elif typeS==CHAT_TYPEPICTURE:
		#insert the picture inside the image table and put the reference as message
		mapInsert['message']="%s"%UploadImage(fromuser,message,"%s"%PHOTOTYPE_CHAT)
        
	mapInsert[KEY_RESULT]= Insert('chatlog',mapInsert)
	if mapInsert[KEY_RESULT]==-1 :
		mapInsert[KEY_ESIT]=ESIT_ERROR
	else:	
		mapInsert[KEY_ESIT]=ESIT_OK
		mapInsert[KEY_RESULT]=SelectS("Select * FROM chatlog WHERE id=%s"%(mapInsert[KEY_RESULT]))
	return mapInsert

def GetChats(fromuser,userid,chatid):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
	if chatid=='-1' :
		sql="SELECT *,chatlog.user2 as touser,user1 as fromuser FROM chatlog where id>%s AND ((user1='%s' AND user2='%s') OR (user1='%s' AND user2='%s'))  AND chatvisible=1 order by datesend DESC limit 0,30;"%(chatid,userid,fromuser,fromuser,userid)
	elif chatid=='0':
		sql="SELECT *,chatlog.user2 as touser,user1 as fromuser FROM chatlog where id>%s AND ((user1='%s' AND user2='%s') OR (user1='%s' AND user2='%s')) and dateview IS NULL  AND chatvisible=1 order by datesend DESC;"%(chatid,userid,fromuser,fromuser,userid)
	else:
		sql="(SELECT *,chatlog.user2 as touser,user1 as fromuser FROM chatlog where id<%s AND ((user1='%s' AND user2='%s') OR (user1='%s' AND user2='%s'))  AND chatvisible=1  order by datesend DESC limit 0,30) UNION (SELECT *,chatlog.user2 as touser,user1 as fromuser FROM chatlog where id>%s AND ((user1='%s' AND user2='%s') OR (user1='%s' AND user2='%s')) and dateview AND chatvisible=1 IS NULL order by datesend DESC);"%(chatid,userid,fromuser,fromuser,userid,chatid,userid,fromuser,fromuser,userid)
	dicti={}
        try:
                rowcount=cursor.execute(sql)
                results=cursor.fetchall()
                dicti[KEY_ESIT]=ESIT_OK
                results=DateToLong(results)
                resultA=[]
		for row in results:
                        #if 'datesend' in row:
                        #        row['date_send']=TimeUtc(row['datesend'])#time.mktime(row['datesend'].timetuple())
                        #        #row['date_last']=time.mktime(dl.timetuple())
			#	del row['datesend']
                        #if 'dateview'in row: 
			#	if row['date_view']!=None: row['date_view']=time.mktime(row['dateview'].timetuple())
			#	del row['dateview']
                        #if 'password' in row: del row['password']
                        if row['type']==CHAT_TYPEPICTURE:
				row['photoid']=int(row['message'])
				row['message']=ResizeImg64(GetAnyPicture(row['message'],'false'),322,60)
			resultA.append(row)
                dicti[KEY_RESULT]=resultA
        except:
                dicti[KEY_ESIT]=ESIT_ERROR

        cursor.close()
        #db.close()
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="UPDATE chatlog SET dateview=now() where user2='%s' AND user1='%s'"%(userid,fromuser)
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
	cursor.close()
	db.close()

	return dicti

#-------------------------------------------------------------------------
#--------------
def DeleteChat(fromuser,touser):
	sql="UPDATE chatlog SET chatvisible=0 WHERE (user1=%s AND user2=%s)OR(user2=%s AND user1=%s)"%(fromuser,touser,fromuser,touser)
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        userid=-1
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except:
                db.rollback()
        cursor.close()
        db.close()
	dicti={}
	dicti[KEY_ESIT]=ESIT_OK
	dicti[KEY_RESULT]=userid
	return dicti
