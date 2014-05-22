#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import json
import string
import urllib2
import urllib
import cStringIO
import base64
#import the file with all the common constansts
from defs import *
from database import *
import utility
#----------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def InsertDeleteTeams(userid,addedteams,deletedteams):
	#utility.ErrorLog("%s %s %s"%(userid,addedteams,deletedteams))
	retD={}
	try:
		addedA=json.loads(addedteams)
		deletedA=json.loads(deletedteams)
		inserted=[]
		deleted=[]
		for row in addedA:
			mapI={}
			mapI['user_uid']=userid
			mapI['team_id']=row
			insD={}
			insD['id_insert']=Insert('user_team',mapI)
			insD['inserted']=mapI
			inserted.append(insD)
		for row in deletedA:
                	mapI={}
                	mapI['user_uid']=userid
                	mapI['team_id']=row
                	insD={}
                	insD['id_deleted']=QueryS("DELETE from user_team WHERE user_uid='%s' AND team_id='%s'"%(userid,row))
                	insD['deleted']=mapI
                	deleted.append(insD)
		retD['added']=inserted
		retD['deleted']=deleted
		retD[KEY_ESIT]=ESIT_OK
	except Esception,e:
		utility.ErrorLog("UpdateTeams, exception:%s"%s)
		retD[KEY_ESIT]=ESIT_ERROR
	return retD

#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def ReturnLeagues():
	db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
	sql="SELECT * FROM league WHERE active=1;"
	dicti={}
	try:
		rowcount=cursor.execute(sql)
		results=cursor.fetchall()
		resultA=[]
                for row in results:
			sportName=''
			#if 'espn_uid' in row: del row['espn_uid']
			if 'sport' in row: 
				sportName=row['sport']
				del row['sport']
				row['sport']=sportName[:-2]
			resultA.append(row)
		dicti[KEY_ESIT]=0
		dicti[KEY_RESULT]=resultA
	except:
		dicti[KEY_ESIT]=2
	
	cursor.close()
        db.close()
        return dicti

#----------------------------------------------------------------------------------------------
#--------------------------------------------------

def ReturnTeams(espnId):
	db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT * FROM team WHERE league_espn_id='%s' ORDER BY location;"%espnId
        dicti={}
        try:
                rowcount=cursor.execute(sql)
                results=cursor.fetchall()
		resultsA=[]
		if espnId=="10" or espnId=="28" or espnId=="23" or espnId=="90" or espnId=="46":
			for row in results:
				row['name']=row['location']+" "+row['name']
				resultsA.append(row)
		else:
			resultsA=results
                dicti[KEY_ESIT]=0
                dicti[KEY_RESULT]=resultsA
        except:
                dicti[KEY_ESIT]=2

        cursor.close()
        db.close()
        return dicti

#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def LikeTeam(useruid,teamid):
	dicti={}
	dicti['user_uid']=useruid
	dicti['team_id']=teamid
	insertedId=Insert('user_team',dicti)
	if insertedId==-1:
		dicti[KEY_ESIT]=2
	else:
		dicti[KEY_ESIT]=0
		dicti[KEY_RESULT]=insertedId
	return dicti

#----------------------------------------------------------------------------------------------
#--------------------------------------------------
