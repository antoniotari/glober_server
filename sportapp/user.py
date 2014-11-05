#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import json
import base64
import random
import string
import urllib2
#import the file with all the common constansts
from defs import *
from database import *
from pictures import *
from utility import ErrorLog,TimeUtc,DateToLong,RemovePassword
import images

DEFAULTMARKER_URL="http://162.216.4.195/sex/defaultmarker.png"

#----------------------------------------------------------------------------------------------
#----------
def SearchUser(sS,uid):
	dictiR={}       
        try:
		sS="{\"data\":%s}"%sS
        	sD=json.loads(sS)
        	sA=sD['data']
        	searchS=''
        	#for row in sA:
                #	searchS=row+" "+searchS
		#searchS=searchS[:-1]
		results2=[]
		for searchS in sA:
			searchS=searchS.lower()

        		results=SelectS("(SELECT user.*,1 as isFollow FROM  user,follow WHERE follow.user_uid = "+ uid +" AND follow.follow_user_uid =user.uid AND follow.isfollowing=1 AND (LOWER(user.username) like '%"+searchS+"%' OR LOWER(user.firstname) like '%"+searchS+"%' OR LOWER(user.lastname) like '%"+searchS+"%' OR LOWER(user.email) like '%"+searchS+"%') AND user.uid != "+ uid +" GROUP BY user.uid) UNION (SELECT user.*,0 as isFollow FROM  user,follow WHERE user.uid !="+ uid +" AND (LOWER(user.username) like '%"+searchS+"%' OR LOWER(user.firstname) like '%"+searchS+"%' OR LOWER(user.lastname) like '%"+searchS+"%' OR LOWER(user.email) like '%"+searchS+"%') AND (user.uid) NOT IN(SELECT follow.follow_user_uid FROM follow WHERE follow.user_uid = "+ uid +") GROUP BY user.uid)")

			results=RemovePassword(results)
                	for row in results:
                        	row['isonline']=IsOnline("%s"%row['uid'])
				row['icon']=DEFAULTMARKER_URL#"http://162.216.4.195/sex/defaultmarker.png"
				present=False
				for row2 in results2:	
					if row['uid']==row2['uid']: present=True 
				if present==False: results2.append(row)
                dictiR[KEY_RESULT]=results2#DateToLong(results)
                dictiR[KEY_ESIT]=ESIT_OK
        except Exception, s:
                dictiR[KEY_ESIT]=ESIT_ERROR
		ErrorLog('file user, SearchUser :%s'%s)
        return dictiR


#----------------------------------------------------------------------------------------------
#----------
def GetPeopleMap(uid,latitude,longitude,maxpeople):
	if maxpeople==None : maxpeople=MAX_PEOPLE
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        #db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
	queryPeople="(SELECT user.*,1 as isFollow,( 3959 * acos( cos( radians("+latitude+") ) * cos( radians( user.latitude ) ) * cos( radians( user.longitude ) - radians("+longitude+") ) + sin( radians("+latitude+") ) * sin( radians( user.latitude ) ) ) ) AS distance FROM  user,follow WHERE user.showlocation=1 AND follow.user_uid = "+ uid +" AND (user.latitude!=0 OR user.longitude!=0) AND follow.follow_user_uid =user.uid AND follow.isfollowing=1 AND user.uid != "+ uid +" GROUP BY user.uid Order By distance) UNION (SELECT user.*,0 as isFollow,( 3959 * acos( cos( radians("+latitude+") ) * cos( radians( user.latitude ) ) * cos( radians( user.longitude ) - radians("+longitude+") ) + sin( radians("+latitude+") ) * sin( radians( user.latitude ) ) ) ) AS distance FROM  user,follow WHERE user.showlocation=1 AND (user.latitude!=0 OR user.longitude!=0) AND user.uid !="+ uid +" AND (user.uid) NOT IN(SELECT follow.follow_user_uid FROM follow WHERE follow.user_uid = "+ uid +") GROUP BY user.uid Order By distance limit "+maxpeople+")";
	
	dictiR={}	
	try:
                queryEsit=cursor.execute(queryPeople)
                results=cursor.fetchall()
		resultA=[]
                for row in results:
			row['icon']=row['marker']#DEFAULTMARKER_URL#"http://162.216.4.195/sex/defaultmarker.png"
		#	if 'registersince'in row: row['registersince']=TimeUtc(row['registersince'])
		#	if 'lastonline'in row: row['lastonline']=TimeUtc(row['lastonline'])
		#	if 'dob'in row: row['dob']=TimeUtc(row['dob'])
        	#	#row['isonline']=IsOnline("%s"%row['uid'])	
		#	resultA.append(row)
		results=RemovePassword(results)
		dictiR[KEY_RESULT]=DateToLong(results)#resultA
		dictiR[KEY_ESIT]=ESIT_OK
	except:
		dictiR[KEY_ESIT]=ESIT_ERROR
        cursor.close()
        db.close()
	return dictiR



#----------------------------------------------------------------------------------------------
#----------SELECT * FROM x WHERE ts BETWEEN timestamp(DATE_SUB(NOW(), INTERVAL 30 MINUTE)) AND timestamp(NOW())
def IsOnline(userid):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
	sql="SELECT count(*) as total FROM user WHERE uid="+userid+" AND lastonline BETWEEN timestamp(DATE_SUB(NOW(), INTERVAL 10 MINUTE)) AND timestamp(NOW())"        
	rowcount=0
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                dicti=results[0]
                rowcount=dicti['total']
        except:
                rowcount=0
        cursor.close()
        db.close()
        if rowcount>0:
                return True
        else:
                return False

#----------------------------------------------------------------------------------------------
#----------
def AddIsOnline(queryAr):
	if type(queryAr) is dict:
		queryAr['isonline']=IsOnline("%s"%queryAr['uid'])
                return queryAr
        elif is_array(queryAr):
                resultAr=[]
                for row in queryAr:
			row['isonline']=IsOnline("%s"%row['uid'])
                	resultAr.append(row)
                return resultAr

#----------------------------------------------------------------------------------------------
#----------
def UploadImage(userid,image64,typeImg):
	mapInsert={}
	mapInsert['user_uid']=userid
	mapInsert['picture64']=urllib2.unquote(image64.decode('utf8')) #ResizeImg64(urllib2.unquote(image64.decode('utf8')))
	try:
		mapInsert['thumb64']=CropResizeImg64(urllib2.unquote(image64.decode('utf8')),THUMB_PIC_W,THUMB_PIC_H)
	except Exception,exc:
		ErrorLog("UploadImage : %s"%exc)
		mapInsert['thumb64']="Unexpected error:"#+ sys.exc_info()[0]	
	mapInsert['phototype']=typeImg
	#save the marker
	try:
		if typeImg=='2' or typeImg==2:
			images.CreateFrame(image64,userid)
	except Exception,exc2:
                ErrorLog("UploadImage, cant creare marker : %s"%exc2)
	return Insert('userimages',mapInsert)

#----------------------------------------------------------------------------------------------
#----------
def UserImage(userid,thumb):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
	sql=''
	key=''
	if thumb==False:
    		key='picture64'
		sql="SELECT %s,id FROM userimages where user_uid='%s' AND phototype=%d order by userimages.date DESC;"%(key,userid,PHOTOTYPE_PROFILE)
    	else:
		key='thumb64'
		sql="SELECT %s,id FROM userimages where user_uid='%s'  AND phototype=%d order by userimages.date DESC;"%(key,userid,PHOTOTYPE_PROFILE)	
	dicti={}
	#encodedimg=''
    	try:
        	rowcount=cursor.execute(sql)
        	results=cursor.fetchall()
		#dicti={}
        	dicti[KEY_RESULT]=results[0]
		dicti[KEY_ESIT]=ESIT_OK
        	#encodedimg=dicti[key]
    	except:
		dicti[KEY_ESIT]=ESIT_ERROR
        	#return ''
    	finally:
       	 	cursor.close()
        	db.close()
        	return dicti#encodedimg


#----------------------------------------------------------------------------------------------
#----------
def UserImageCover(userid,thumb):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql=''
        key=''
        if thumb==False:
                key='picture64'
                sql="SELECT %s,id FROM userimages where user_uid='%s' AND phototype=%d order by userimages.date DESC;"%(key,userid,PHOTOTYPE_COVER)
        else:
                key='thumb64'
                sql="SELECT %s,id FROM userimages where user_uid='%s'  AND phototype=%d order by userimages.date DESC;"%(key,userid,PHOTOTYPE_COVER)
        
	#encodedimg=''
        dicti={}
	try:
                rowcount=cursor.execute(sql)
                results=cursor.fetchall()
                #dicti={}
                dicti[KEY_RESULT]=results[0]
                dicti[KEY_ESIT]=ESIT_OK
                #encodedimg=dicti[key]
        except:
		dicti[KEY_ESIT]=ESIT_ERROR
                #return ''
        finally:
                cursor.close()
                db.close()
                return dicti#encodedimg

#----------------------------------------------------------------------------------------------
#----------
def ReturnUserFromId(userid):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        #db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT * FROM user where uid='"+userid+"';"
        dicti={}
        try:
                rowcount=cursor.execute(sql)
                results=cursor.fetchall()
                #dicti=results[0]
                dicti=DateToLong(results[0])
		dicti=RemovePassword(dicti)
		dicti=AddIsOnline(dicti)
		#if 'lastonline' in dicti: del dicti['lastonline']
                #if 'password' in dicti: del dicti['password']
		#if 'registersince' in dicti: del dicti['registersince']
        except:
                return dicti
        finally:
                cursor.close()
                db.close()
		results=ReturnUserTeams(userid)
		dicti['teams']=results
                return dicti

#----------------------------------------------------------------------------------------------
#----------
def ReturnUserUidFromEmail(email):
        sql="SELECT uid FROM user where email='%s';"%email
        try:
		return SelectS(sql)[0]['uid']
        except:
                return -1


#----------------------------------------------------------------------------------------------
#---------- return all the teams the user has selected
def ReturnUserTeams(userid):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        #sql="SELECT team .* FROM  `user_team` , user, team WHERE user.uid="+userid+" AND user_team.`user_uid` = user.uid AND user_team.`team_id` = team.id;"
	sql="SELECT team . * , league.name AS league_name, league.abbreviation AS league_abbreviation, league.shortName AS league_shortname, league.apilink AS league_apilink FROM  `user_team` , user, team, league WHERE user.uid ="+userid+" AND user_team.`user_uid` = user.uid AND user_team.`team_id` = team.id AND team.league_espn_id = league.espn_id AND user_team.following=1 GROUP BY id;"
	results=[]
        try:
                rowcount=cursor.execute(sql)
                results=cursor.fetchall()
                #desc=cursor.description
                #i=0
                #for row in results:
               	#	i=i+1
		#	username=row['username']
                
        except:
 		results=[]
	cursor.close()
        db.close()
        return results


#----------------------------------------------------------------------------------------------
#----------
def ChangePassword(newPass,userid):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="UPDATE user set password='"+newPass+"' where uid='"+userid+"';"
        dicti={}
        try:
                rowcount=cursor.execute(sql)
                db.commit()
		return 0
        except:
		db.rollback()
                return 2
       
	cursor.close()
        db.close()
        return dicti

#----------------------------------------------------------------------------------------------
#----------
def UpdatePassword(newPass,oldPass,userid):
	if oldPass==None:oldPass=''
	dicti={}
	dicti['password']=oldPass
	dicti['uid']=userid
	if exists('user',dicti):
		return ChangePassword(newPass,userid)
	return 1
#print "Content-type:application/json\r\n\r\n"
#print UserImage('5718',False)
