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
from user import ReturnUserTeams
from user import ReturnUserFromId
from pictures import CropResizeImg64,JpgToPng64
from database import QueryS,exists,existsS
import database
from utility import ErrorLog,encodedb,id_generator
import images
import emailsend

FB_GRAPH_URL=	"https://graph.facebook.com/"
FB_PIC_W=	'444'
FB_PIC_H=	'444'
FB_THUMB_D=	'111'

#----------------------------------------------------------------------------------------------

def SignUpFbToken(token):
	#ErrorLog("inside function SignUpFbToken token: %s"%s)
	resultFbJ={}
	d={}
	d=urllib2.urlopen(FB_GRAPH_URL+"me?access_token="+token).read()
	resultFbJ=json.loads(d)

	fbID=''
	try:
		fbID=resultFbJ['id']
	except Exception ,e:
		ErrorLog("SignUpFbToken error:%s"%e)
		return 'cant find id maybe wrong token'
	
	email=''
	try:
		email=resultFbJ['email']
	except Exception ,el:
                ErrorLog("SignUpFbToken, email from fb error:%s %s"%(el,d))
		#return 'cant find email maybe wrong token'
		email="%s@facebook.com"%(resultFbJ['id'])
	
	#check if the email is present in the database
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
    	sql="SELECT count(*) as total FROM user where email='"+email+"';"
    	rowcount=0
    	try:
        	queryEsit=cursor.execute(sql)
        	results=cursor.fetchall()
        	dicti=results[0]
        	rowcount=dicti['total']
    	except Exception,fe:
		ErrorLog("SignUpFbToken, email exixts exc : %s"%fe)
		cursor.close()
                db.close()
        	return 'error exception reading database: %s'%fe
    	finally:
        	cursor.close()
        	db.close()
	
	dictReturn={}
	if rowcount==0:
		dictReturn=AddUserFb(fbID,email,resultFbJ)
                dictReturn['new_user']=True
	elif rowcount>0:
		dictReturn=ReturnUser(email)
		dictReturn['new_user']=False
	
	#save the token into the table
	useruid=dictReturn['uid']
	try:
		SaveToken("%s"%useruid,token)#SaveToken(token,0,useruid)
	except Exception, er:
		ErrorLog('SignUpFbToken, facebook login save token: %s'%er)
	return dictReturn


#----------------------------------------------------------------------------------------------
#----------
def SaveToken_old(token,typeToken,useruid):#typeToken is 0 for facebook token , 1 for twitter token
	#check if the token is present in the database
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT count(*) as total FROM accesstoken where accesstoken='"+token+"';"
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
	if rowcount>0:return

	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="INSERT INTO accesstoken (accesstoken,type,user_uid) VALUES ('%s',%d,%d);"%(token,typeToken,useruid)
        try:
                cursor.execute(sql)
                db.commit()
        except:
                db.rollback()
	cursor.close()
        db.close()

#----------------------------------------------------------------------------------------------
#----------
def SaveToken(uid,fbt):
	try:
        	if database.existsS('accesstoken','user_uid',uid)==False:
                	mapI={}
                	mapI['accesstoken']=fbt
                	mapI['user_uid']=uid
                	database.Insert('accesstoken',mapI)
        	else:
                	mapex={}
                	mapex['user_uid']=uid
                	mapex['accesstoken']=fbt
                	if database.exists('accesstoken',mapex)==False:
                        	database.QueryS("UPDATE accesstoken SET accesstoken='%s' WHERE user_uid='%s';"%(fbt,uid))
	except Exception, f:
		ErrorLog("SaveToken , error: %s"%f)



#----------------------------------------------------------------------------------------------
#----------
def LoginTwitter(username,email,twitterId,tokentwit):
        #first of all check if the user is already present into the database
        if exists('user','email',email):
                d={}
		d= ReturnUser(email)
		useruid=d['uid']
		SaveToken(token,1,useruid)
                #d['description']='the user is already registered'
                d['esit_register']=1
                return d
        #if the user is not present...
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="INSERT INTO user (username,email,twitterid) VALUES ('%s','%s','%s');"%(username,email,twitterId)
        userid=0
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except:
                db.rollback()
        cursor.close()
        db.close()

        d= ReturnUser(email)
        d['esit_register']=0
	
	useruid=d['uid']
        SaveToken(token,1,useruid)

        return d

#----------------------------------------------------------------------------------------------
#----------
def UserUpdate(userid,username,password,firstname,lastname,gender,nationality,dob,latitude,longitude,currentcity,hometown,fbid,twitterid,occupation,aboutme,relationship,state,active,showlocation):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="UPDATE `user` SET username=%s,password=%s,firstname=%s,lastname=%s,gender=%s,nationality=%s,dob=%s,latitude=%s,longitude=%s,currentcity=%s,hometown=%s,fbid=%s,twitterid=%s,occupation=%s,aboutme=%s,relationship=%s,state=%s,active=%s,showlocation=%s WHERE uid=%s"%(validateUserData(username,'username',userid),validateUserData(password,'password',userid),validateUserData(firstname,'firstname',userid),validateUserData(lastname,'lastname',userid),validateUserData(gender,'gender',userid),validateUserData(nationality,'nationality',userid),validateUserData(dob,'dob',userid),validateUserData(latitude,'latitude',userid),validateUserData(longitude,'longitude',userid),validateUserData(currentcity,'currentcity',userid),validateUserData(hometown,'hometown',userid),validateUserData(fbid,'fbid',userid),validateUserData(twitterid,'twitterid',userid),validateUserData(occupation,'occupation',userid),validateUserData(aboutme,'aboutme',userid),validateUserData(relationship,'relationship',userid),validateUserData(state,'state',userid),validateUserData(active,'active',userid),validateUserData(showlocation,'showlocation',userid),userid)
        valueToGet=''
        try:
                queryEsit=cursor.execute(sql)
		db.commit()
        except Exception ,e:
		db.rollback()
                cursor.close()
        	db.close()
		d=ReturnUser(getValue('user','email','uid',userid))
		d[KEY_ESIT]=ESIT_ERROR
		d['error']='user not updated %s'%e
		ErrorLog('user not updated %s'%e)
		return d
        cursor.close()
        db.close()
	d=ReturnUser(getValue('user','email','uid',userid))
        d[KEY_ESIT]=ESIT_OK
        return d

#----------------------------------------------------------------------------------------------
#----------
def validateUserData(value,key,userid):
	valueToInsert=value
	if value==None:
		valueToInsert=getValue('user',key,'uid',userid)
		if valueToInsert==None:	
			return 'NULL'
	return "'%s'"%encodedb("%s"%valueToInsert)


#----------------------------------------------------------------------------------------------
#----------
def getValue(table,keyToGet,key,value):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT "+keyToGet+" FROM "+table+" WHERE "+key+"='"+value+"';"
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


#----------------------------------------------------------------------------------------------
#----------
def exists(table,key,value):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT count(*) as total FROM "+table+" WHERE "+key+"='"+value+"';"
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
#----------check if an element into the table exists
def existsD(table,hashMap):
        #form the sql statement
        whereStat=' WHERE '
        for key, value in hashMap.iteritems():
                whereStat="%s%s='%s' AND "%(whereStat,key,value)
                #whereStat=whereStat+key+"='"+value+"' AND "
        #sql="SELECT count(*) as total FROM "+table+whereStat[:-5]+";"
        sql="SELECT count(*) as total FROM %s%s"%(table,whereStat[:-5])
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        #db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        rowcount=0
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                dicti=results[0]
                rowcount=dicti['total']
        except Exception,e:
                ErrorLog("database,exists, %s"%e)
                rowcount=0
        cursor.close()
        db.close()
        if rowcount>0:
                return True
        else:
                return False


#----------------------------------------------------------------------------------------------
#----------
def AddUserFb(fbID,email,resultFbJ):	
	#----if the user doesnt exists save the picture----
	fbPic=FB_GRAPH_URL+fbID+"/picture?width="+FB_PIC_W+"&height="+FB_PIC_H
	fbThumb=FB_GRAPH_URL+fbID+"/picture?width="+FB_THUMB_D+"&height="+FB_THUMB_D	
	fbCover="http://graph.facebook.com/%s?fields=cover"%fbID
	encodedPic=''
	try:
		encodedPic =JpgToPng64(base64.b64encode(urllib.urlopen(fbPic).read()))
	except:
		encodedPic=''
		
	encodedThumb=''
	try:
		encodedThumb =JpgToPng64(base64.b64encode(urllib.urlopen(fbThumb).read()))
	except:
		encodedThumb=''
	
	encodedCover=''
	try:
		dCover=json.loads(urllib.urlopen(fbCover).read())
                encodedCover =JpgToPng64(base64.b64encode(urllib.urlopen(dCover['cover']['source']).read()))
	except:
		encodedCover=''
	#----
	
	username=Val(resultFbJ,'username')
	first_name=Val(resultFbJ,'first_name')
	last_name=Val(resultFbJ,'last_name')
	genderS=Val(resultFbJ,'gender')
	gender=0
	if genderS=='female':
		gender=1
	birthday=Val(resultFbJ,'birthday')
	location=''
	hometown=''
	
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
	sql="INSERT INTO user (username,email,firstname,lastname,gender,dob,hometown,currentcity,fbid) VALUES ('%s','%s','%s','%s','%d','%s','%s','%s','%s');"%(username,email,first_name,last_name,gender,birthday,hometown,location,fbID)
	userid=0
    	try:
    		cursor.execute(sql)
        	userid=db.insert_id()
		db.commit()
	except:
        	db.rollback()
        	return 'error inserting into user table function:AddUserFb'
        cursor.close()
        #db.close()
       
	#create the marker for the user
	try:
                images.CreateFrame(encodedPic,userid)
        except Exception,exc2:
                ErrorLog("login.py adduserfb, cant creare marker : %s"%exc2)
 
    	sql="INSERT INTO userimages (user_uid,phototype,picture64,thumb64)VALUES('%d','2','%s','%s');"%(userid,encodedPic.decode('string_escape'),encodedThumb.decode('string_escape'))
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
	try:
    		cursor.execute(sql)
        	db.commit()
    	except:
        	db.rollback()
        cursor.close()
	
	#insert the cover into the database
	sql="INSERT INTO userimages (user_uid,phototype,picture64,thumb64)VALUES('%d','4','%s','%s');"%(userid,encodedCover.decode('string_escape'),CropResizeImg64(encodedCover,220,150))
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        try:
                cursor.execute(sql)
                db.commit()
        except:
                db.rollback()
        cursor.close()

        db.close()
    
    	return ReturnUser(email)
    
#----------------------------------------------------------------------------------------------
#----------
def ReturnUser_old(email):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
#	db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
    	sql="SELECT * FROM user where email='"+email+"';"
    	dicti={}
    	try:
        	rowcount=cursor.execute(sql)
        	results=cursor.fetchall()
        	dicti=results[0]
        	if 'registersince' in dicti: del dicti['registersince']
    	except:
		cursor.close()
                db.close()
        	return dicti
    	finally:
        	cursor.close()
        	db.close()
		useruid=getValue('user','uid','email',email)
		teams=ReturnUserTeams(useruid)
		dicti['teams']=teams
        	return dicti

#----------------------------------------------------------------------------------------------
#----------
def ReturnUser(email):
	useruid=getValue('user','uid','email',email)
	dicti=ReturnUserFromId("%d"%useruid)
	return dicti
#----------------------------------------------------------------------------------------------
#----------
def RegisterUser(username,email,password):
        #first of all check if the user is already present into the database
	if exists('user','email',email):
		d={}
		d['description']='the email is already registered'
		d['esit_register']=1
		return d
	
	if username==None:username=id_generator()
	if existsS('user','username',username):
                d={}
                d['description']='the username is already registered'
                d['esit_register']=3
                return d

	#if the user is not present...
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="INSERT INTO user (username,email,password,active) VALUES ('%s','%s','%s',1);"%(username,email,password)
        userid=0
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except:
                db.rollback()
        cursor.close()
        db.close()
	try:
		emailsend.sendemail(email)
	except Exception ,ems:
		ErrorLog("RegisterUser %s %s %s , exception:%s"%(username,email,password,ems))
	d= ReturnUser(email)
	d['esit_register']=0
	return d
    
#----------------------------------------------------------------------------------------------
#----------
def LoginUser_old(email,password):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT * FROM user where email='"+email+"' AND password='"+password+"';"
        dicti={}
        try:
                rowcount=cursor.execute(sql)
                results=cursor.fetchall()
                dicti=results[0]
                if 'registersince' in dicti: del dicti['registersince']
		if 'lastonline' in dicti: del dicti['lastonline']
		if 'password' in dicti: del dicti['password']
		dicti[KEY_ESIT]=ESIT_OK
        except:
                #cursor.close()
                #db.close()
		#return dicti
		dicti[KEY_ESIT]=ESIT_ERROR
		dicti['exception']='exception loginuser'
        finally:
                cursor.close()
                db.close()
                return dicti


#----------------------------------------------------------------------------------------------
#----------
def LoginUser(email,password):
#	results=SelectS("SELECT * FROM user where email='%s' AND password='%s';"%(email,password))
	dictE={}
	dictE['password']=password
	dictE['email']=email
	dictReturn={}
        if existsD('user',dictE):
        	dictReturn=ReturnUser(email)
		dictReturn[KEY_ESIT]=ESIT_OK
	else:
		dictReturn[KEY_ESIT]=ESIT_EXIST
	return dictReturn

#----------------------------------------------------------------------------------------------
#----------
def Val(dicti,key):
	try:
		value=dicti[key]
		return value
	except:
		return ''


def main():
        print "Content-type:application/json\r\n\r\n"
        print SignUpFbToken('CAAHqrnAb1n8BAKExZC0GJlMPAKdVnQgUc6T1EK3IIIuDZAtbZCvmEAn5H2ZB0ZCeTUC41b4sZAeuihjRUgdRaZAEiRH6AL4VO1sDas9yBYn498dnKarGmZC6mh82YcAcuGukmlAWiNqrNmWJxYWIwSzAPMUXrL8YhK6775wKHoCoOH8uyaZC12Li7zGQLHSCaveDlWbwWJU8IEogtZBqZAs1hZBd')

#----------------------------------------------------------------------------
#-----START the script

if __name__ == '__main__':
    main()

#----------------------------------------------------------------------------


