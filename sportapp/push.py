#!/usr/bin/python
import MySQLdb
import json
import base64
import random
import string
from py4j.java_gateway import JavaGateway

from defs import *
from database import *
from utility import ErrorLog
#--------------------------------------------------------------------
#-----  
def SendPush_old(deviceS,fromS,to,typeS,message):
	if deviceS==None :
		resultDe=SelectS("SELECT devicetype,devicetoken from device,user WHERE user.uid=user_uid and user.uid='%s' ORDER BY ID DESC"%(to))	
		deviceS=resultDe[0]['devicetype']

	responseJ={}
        fromUsername=UsernameFromId(fromS)
        tokenToUse=GetToken(to)
        dev=True
        if(deviceS=='iph'):
        	dev=isDevelopment(tokenToUse)
#               return 'hello'+fromUsername+tokenToUse
        gateway = JavaGateway()
        responseA=[]
        i=0
        #return json.dumps(responseA)
        for row in tokenToUse:
        	responseS=gateway.entry_point.SendPush(deviceS,""+fromS,""+to,typeS,message,row,fromUsername,GOOGLE_API_KEY,dev)
                d={}
                try:
                	d=json.loads(responseS)
                except:
                        d=responseS
                responseA.append(d)
                i=i+1
	responseJ['fromId']=fromS
        responseJ['toId']=to
        responseJ['fromUsername']=fromUsername
        responseJ[KEY_ESIT]=0
        responseJ[KEY_RESULT]=responseA
        #return json.dumps(responseJ)
	return responseJ	

#--------------------------------------------------------------------
#-----  
def SendPush(deviceS,fromS,to,typeS,message):
	resultDe=SelectS("SELECT devicetype,devicetoken,development from device,user WHERE user.uid=user_uid and user.uid='%s' ORDER BY ID DESC"%(to))
        responseJ={}
        fromUsername=UsernameFromId(fromS)
        gateway = JavaGateway()
        responseA=[]
        i=0
	isIosDev=False
        for row in resultDe:
                devTy=row['devicetype']
		#responseS=gateway.entry_point.SendPush(devTy,""+fromS,""+to,typeS,message,row['devicetoken'],fromUsername,GOOGLE_API_KEY,isIosDev)#row['development'])
		responseS="{\"esit\"=0}"
		#if it fails for ios try resending it in development mode
		#try:
		#	if devTy=='ios':
		#		if json.loads(responseS)[KEY_ESIT]==ESIT_ERROR:
		#			responseS=gateway.entry_point.SendPush(devTy,""+fromS,""+to,typeS,message,row['devicetoken'],fromUsername,GOOGLE_API_KEY,not isIosDev)
		#except Exception,fgex:
		#	ErrorLog("push.py,SendPush: %s"%fgex)
		d={}
                try:
                        d=json.loads(responseS)
                except Exception, dexc:
			ErrorLog("push.py,SendPush: %s"%dexc)
                        d=responseS
                responseA.append(d)
                i=i+1
        responseJ['fromId']=fromS
        responseJ['toId']=to
        responseJ['fromUsername']=fromUsername
        responseJ[KEY_ESIT]=0
        responseJ[KEY_RESULT]=responseA
        #return json.dumps(responseJ)
        return responseJ



#--------------------------------------------------------------------
#--------------------------------------------------------------------
#-----
def isDevelopment(token):
	return True
  
#--------------------------------------------------------------------
#-----  
def UsernameFromId(uid):
	username=''
	sql="SELECT username FROM user WHERE uid ="+uid
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
        try:
        	cursor.execute(sql)
 		results=cursor.fetchall()
                desc=cursor.description
                i=0
                for row in results:
                	i=i+1
			username=row['username']
	except:
                username= "a friend"
        finally:
                cursor.close()       
		db.close()
		return username

#--------------------------------------------------------------------
#-----  
def GetToken(uid):
	token=[]#'notoken'
        sql="SELECT devicetoken FROM device WHERE user_uid ="+uid
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
        try:
        	cursor.execute(sql)
                results=cursor.fetchall()
                desc=cursor.description
                i=0
                for row in results:
                	tokenS=row['devicetoken']
			token.append(tokenS)
			i=i+1                                
			#for row2 in row:
                        #       d[row2]="%s"%(row[row2])
                        #       i=i+1
	except:
        	return token
        finally:
                cursor.close()
		db.close()
                return token

#--------------------------------------------------------------------
#-----  
def RegisterToken_old(tokenS,typeS,deviceId,userUid,development,version):
	responseJ={}
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="INSERT INTO device (development,devicetype,deviceid,devicetoken,user_uid,version) VALUES ('%s','%s','%s','%s','%s','%s');"%(development,typeS,deviceId,tokenS,userUid,version)

        try:
        	cursor.execute(sql)
                db.commit()
                responseJ[KEY_ESIT]=ESIT_OK
        except:
                db.rollback()
                responseJ[KEY_ESIT]=ESIT_ERROR
        finally:
                cursor.close()
		db.close()
        return responseJ

#--------------------------------------------------------------------
#----- 
def RegisterToken(tokenS,typeS,deviceId,userUid,development,version):
	if development==None: development='0'
	if version==None: version='0'
	responseJ={}
        sql=''
        mapex={}
        mapex['deviceid']=deviceId
        mapex2={}
	mapex2['devicetoken']=tokenS
	if exists('device',mapex)==True:
        	mapex['devicetoken']=tokenS
                if exists('device',mapex)==False:
                	sql="UPDATE device SET development='%s',devicetoken='%s' WHERE deviceid='%s';"%(development,tokenS,deviceId)
        elif exists('device',mapex2)==True:
		responseJ[KEY_RESULT]='token already present'
	else:
        	sql="INSERT INTO device (development,devicetype,deviceid,devicetoken,user_uid,version) VALUES ('%s','%s','%s','%s','%s','%s');"%(development,typeS,deviceId,tokenS,userUid,version)

	if sql=='':
        	responseJ[KEY_ESIT]=ESIT_EXIST
                return responseJ
	responseJ[KEY_RESULT]=sql
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        try:
        	cursor.execute(sql)
                db.commit()
                responseJ[KEY_ESIT]=ESIT_OK
        except:
        	db.rollback()
                responseJ[KEY_ESIT]=ESIT_ERROR
        finally:
                cursor.close()

        return responseJ



#--------------------------------------------------------------------
#-----  

def main():
        print "Content-type:application/json\r\n\r\n"
	print json.dumps(SendPush('and','5721','5702','c','message'))
#----------------------------------------------------------------------------
#-----START the script

if __name__ == '__main__':
    main()

#----------------------------------------------------------------------------
