#!/usr/bin/python
from database import *
from defs import *
from user import IsOnline
import MySQLdb
from notification import InsertNotification

#----------------------------------------------------------------------------------------------
#-----------insert following
def IAmFollow(useruid,followuseruid):
	db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT count(*) as total FROM `follow`  WHERE follow_user_uid = '%s' AND user_uid='%s';"%(followuseruid,useruid)
        followI=0
        try:
                rowcount=cursor.execute(sql)
                resutA=cursor.fetchall()
                followI=resutA[0]['total']
        except:
                followI=-1

        cursor.close()
        db.close()
        return followI


#----------------------------------------------------------------------------------------------
#-----------delete following
def UnFollow(useruid,followuseruid):
	dicty={}
	try:
		dicty[KEY_RESULT]=QueryS("DELETE FROM follow where user_uid='%s' AND follow_user_uid='%s'"%(useruid,followuseruid))
		dicty[KEY_ESIT]=ESIT_OK
	except Exception,e:
		dicty[KEY_RESULT]="%s"%e
		dicty[KEY_ESIT]=ESIT_ERROR
	return dicty

#----------------------------------------------------------------------------------------------
#-----------insert following
def DoFollow(useruid,followuseruid):
	mapInsert={}
	mapInsert['user_uid']=useruid
	mapInsert['follow_user_uid']=followuseruid
	mapInsert[KEY_RESULT]=Insert('follow',mapInsert)
	if mapInsert[KEY_RESULT]==-1:
		mapInsert[KEY_ESIT]=ESIT_ERROR
	else:
		InsertNotification("You have a new follower",NOTIF_TYPEFOLLOW,useruid,useruid,followuseruid)
		mapInsert[KEY_ESIT]=ESIT_OK
	return mapInsert

#----------------------------------------------------------------------------------------------
#------------see who the user is following
def GetFollowing(useruid):
	db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT user.firstname,user.lastname,user.username, user.uid FROM  `follow` , user WHERE follow_user_uid = user.uid AND user_uid='%s';"%useruid
        dicti={}
        try:
                rowcount=cursor.execute(sql)
                resutA=cursor.fetchall()
                dicti[KEY_ESIT]=ESIT_OK
                dicti[KEY_RESULT]=resutA
        except:
                dicti[KEY_ESIT]=ESIT_ERROR

        cursor.close()
        db.close()
        return dicti

#----------------------------------------------------------------------------------------------
#------------see who is following the user
def GetFollowers(useruid):
	db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT user.firstname,user.lastname,user.username, user.uid FROM  `follow` , user WHERE user_uid = user.uid AND follow_user_uid='%s';"%useruid
        dicti={}
        try:
                rowcount=cursor.execute(sql)
                resutA=cursor.fetchall()
                dicti[KEY_ESIT]=ESIT_OK
                dicti[KEY_RESULT]=resutA
        except:
                dicti[KEY_ESIT]=ESIT_ERROR

        cursor.close()
        db.close()
        return dicti

#----------------------------------------------------------------------------------------------
#------------return who i can chat with, online or offline, username, uid

def GetUserToChat(useruid):
	f1=GetFollowing(useruid)
	f2=GetFollowers(useruid)
	f1A=f1[KEY_RESULT]
	f2A=f2[KEY_RESULT]
	resultA=[]
	for row1 in f1A:
		for row2 in f2A:
			if row1['uid']==row2['uid']:
				#row1['online']=True
				row1['isonline']=IsOnline("%d"%row1['uid'])
				resultA.append(row1)
				
	dicti={}
	dicti[KEY_ESIT]=ESIT_OK
        dicti[KEY_RESULT]=resultA
        return dicti
