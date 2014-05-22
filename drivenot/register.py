#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import json
import base64
import random
import string
#import the file with all the common constansts
from defs import *
#from database import exists,getValue,Insert
import cgi
import cgitb
import hashlib
from datetime import date, timedelta
import datetime

securityString1="OoorteeegfhoodsfhahuibahcbfrtingrtektangdfseWallaetdfwalladdhjybingdsfrbangooppdd"
securityString2="OoorWINTERangdfseWalFORZAINTERgdsfrAAddFFFppdd"

def Authenticate(form):
	secdeviceid=form.getvalue('secdeviceid')
	sectoken=form.getvalue('sectoken')
	secsync=form.getvalue('secsync')
	
	if(sectoken==None):return False
	
	mdS=secdeviceid+securityString1+secsync+securityString2
	m = hashlib.md5()
	m.update(mdS)
	criptedS= m.hexdigest()	
	if criptedS==sectoken: return True
	return False


def Register(form):
	deviceId=form.getvalue('deviceid')
	exB=exists('user',"deviceid",deviceId)
	mapD={}
	if(exB==False):
		mapD['deviceid']=deviceId;
		mapD['phoneData64']=form.getvalue('phoneinfo')
		#save the emails
		mapD['emails64']=form.getvalue('emails')
		mapD['purchase']=1
		mapD[KEY_RESULT]=Insert("user",mapD)
		mapD[KEY_ESIT]=0
	else:
		mapD[KEY_ESIT]=1
        mapD['purchased']=getValue("user","purchase","deviceid",deviceId)
	mapD['date']=getValue("user","dateRegistered","deviceid",deviceId)
        return json.dumps(mapD)

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

#----------get the value from the table where key=value
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
		if isinstance(dicti[keyToGet],datetime.date):
			realdate=dicti[keyToGet]
			d=realdate-timedelta(days=8)
			dicti[keyToGet]=d
                valueToGet="%s"%dicti[keyToGet]
        except:
                valueToGet=''
        cursor.close()
        db.close()
        return valueToGet


#----------------------------------------------------------------------------------------------
#----------get the value from the table where key=value
def getValue2(table,keyToGet,hashMap):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)

        whereStat=' WHERE '
        for key, value in hashMap.iteritems():
                whereStat=whereStat+key+"='"+value+"' AND "
        sql="SELECT "+keyToGet+" FROM "+table+whereStat[:-5]+";"
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

#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def Insert(table,mapInsert):
        #form the where statement
        #whereStat=' WHERE '
        #for key, value in mapConditions.iteritems():
        #       whereStat=whereStat+key+"='"+value+"' AND "
        #the insert statement
        insertStatKeys="INSERT INTO "+table+" ("
        insertStatValues="VALUES("
        for key, value in mapInsert.iteritems():
                insertStatKeys=insertStatKeys+key+","
                insertStatValues=insertStatValues+"'"+value+"',"
        insertStatKeys=insertStatKeys[:-1]+")"
        insertStatValues=insertStatValues[:-1]+")"

        sql=insertStatKeys+insertStatValues#+whereStat
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        userid=-1
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except:
                db.rollback()
        finally:
		cursor.close()
        	db.close()
        return userid


def Purchase(form):
	deviceId=form.getvalue('deviceid')
	if exists("user","deviceid",deviceId)==False:
		Register(form)

	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="UPDATE user SET purchase=1 WHERE deviceid='%s';"%deviceId
	userid=-1
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except:
                db.rollback()
        cursor.close()
        db.close()
        mapD={}
        mapD['purchased']=getValue("user","purchase","deviceid",deviceId)
        mapD[KEY_ESIT]=0
        return json.dumps(mapD)



def main():
	print "Content-type:application/json\r\n\r\n"
	form=cgi.FieldStorage()
	
	#security check
	if Authenticate(form)==False : 
		dd={}
		dd[KEY_ESIT]=2
		dd[KEY_RESULT]="security check failed"
		print json.dumps(dd)
		return "error"

	cmd="%s" % form.getvalue(KEY_CMD)
	#print "here"+cmd+form.getvalue('deviceid')
	if cmd=="register":
        	print Register(form)
	elif cmd=='purchase':
	        print Purchase(form)


#----------------------------------------------------------------------------
#-----START the script

if __name__ == '__main__':
    main()

#----------------------------------------------------------------------------

