#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import json
#import base64
#import random
import string
#import simplejson
#from py4j.java_gateway import JavaGateway

#import the file with all the common constansts
from defs import *
from utility import *

#----------------------------------------------------------------------------------------------
#----------check if an element into the table exists
def exists(table,key,value):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
	sql="SELECT count(*) as total FROM %s WHERE %s='%s';"%(table,key,value)
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
#----------check if an element into the table exists
def existsS(table,key,value):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        #db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        #sql="SELECT count(*) as total FROM "+table+" WHERE "+key+"='"+value+"';"
        sql="SELECT count(*) as total FROM %s WHERE %s='%s';"%(table,key,value)
	rowcount=0
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                dicti=results[0]
                rowcount=dicti['total']
        except Exception,e:
                ErrorLog("database,existsS, %s"%e)
                rowcount=0
        cursor.close()
        db.close()
        if rowcount>0:
                return True
        else:
                return False


#----------------------------------------------------------------------------------------------
#----------check if an element into the table exists
def exists(table,hashMap):
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
#----------get the value from the table where key=value
def getValue(table,keyToGet,key,value):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
	sql="SELECT %s FROM %s WHERE %s='%s';"%(keyToGet,table,key,value)
        #sql="SELECT "+keyToGet+" FROM "+table+" WHERE "+key+"='"+value+"';"
        valueToGet=''
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                dicti=results[0]
                valueToGet=dicti[keyToGet]
        except Exception,e:
                ErrorLog("database,getvalue, %s"%e)
                valueToGet=''
        cursor.close()
        db.close()
        return valueToGet


#----------------------------------------------------------------------------------------------
#----------get the value from the table where key=value
def getValueS(table,keyToGet,key,value):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        #db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        #sql="SELECT "+keyToGet+" FROM "+table+" WHERE "+key+"='"+value+"';"
        sql="SELECT %s FROM %s WHERE %s='%s';"%(keyToGet,table,key,value)
	valueToGet=''
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                if len(results)==0:return ''
		dicti=results[0]
                valueToGet=dicti[keyToGet]
        except Exception,e:
                ErrorLog("database,getvalueS, %s \nquery:%s"%(e,sql))
                valueToGet=''
        cursor.close()
        db.close()
        return valueToGet


#----------------------------------------------------------------------------------------------
#----------get the value from the table where key=value
def getValue(table,keyToGet,hashMap):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
	#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        
	whereStat=' WHERE '
        for key, value in hashMap.iteritems():
                whereStat="%s%s='%s' AND "%(whereStat,key,value)
		#whereStat=whereStat+key+"='"+value+"' AND "
	#sql="SELECT "+keyToGet+" FROM "+table+whereStat[:-5]+";"
        sql="SELECT %s FROM %s%s;"%(keyToGet,table,whereStat[:-5])
	valueToGet=''
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                dicti=results[0]
                valueToGet=dicti[keyToGet]
        except Exception,e:
                ErrorLog("database,getvalue, %s"%e)
                valueToGet=''
        cursor.close()
        db.close()
        return valueToGet

#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def Select(table,hashMap):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
	whereStat=' WHERE '
        for key, value in hashMap.iteritems():
                whereStat="%s%s='%s' AND "%(whereStat,key,value)
		#whereStat=whereStat+key+"='"+value+"' AND "
        #sql="SELECT * FROM "+table+whereStat[:-5]+";"
	sql="SELECT * FROM %s%s;"%(table,whereStat[:-5])
	resultA=[]
        try:
                queryEsit=cursor.execute(sql)
                resultA=DateToLong(cursor.fetchall())
        except Exception,e:
                ErrorLog("database,select, %s"%e)
                resultA=[]
        cursor.close()
        db.close()
        return resultA

#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def SelectS(sql):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        resultA=[]
        try:
                queryEsit=cursor.execute(sql)
                resultA=DateToLong(cursor.fetchall())
        except Exception,e:
                ErrorLog("database,selectS, %s"%e)
                resultA=[]
        cursor.close()
        db.close()
        return resultA


#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def Insert(table,mapInsert):
        #the insert statement
        #insertStatKeys="INSERT INTO "+table+" ("
        insertStatKeys="INSERT IGNORE INTO %s ("%(table)
	insertStatValues="VALUES("
        for key, value in mapInsert.iteritems():
                insertStatKeys="%s%s,"%(insertStatKeys,key)
		insertStatValues="%s'%s',"%(insertStatValues, encodedb("%s"%value))
		#insertStatKeys=insertStatKeys+key+","
                #insertStatValues=insertStatValues+"'"+"%s"%value+"',"
        insertStatKeys="%s)"%(insertStatKeys[:-1])
	insertStatValues="%s)"%(insertStatValues[:-1])
	#insertStatKeys=insertStatKeys[:-1]+")"
        #insertStatValues=insertStatValues[:-1]+")"
	
        sql="%s%s"%(insertStatKeys,insertStatValues)#+whereStat
        #db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
 
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        userid=0
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except Exception,e:
                db.rollback()
		if e[0]==1062 : userid=-3
		else: userid=-1
		ErrorLog("database Insert, error:%s"%e)
        cursor.close()
        db.close()
        return userid

#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def Delete(table,hashMap):
	whereStat=' WHERE '
        for key, value in hashMap.iteritems():
                whereStat="%s%s='%s' AND "%(whereStat,key,value)
		#whereStat=whereStat+key+"='"+value+"' AND "
        sql="DELETE FROM "+table+whereStat[:-5]+";"

        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        userid=-1
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except Exception,e:
        	db.rollback()
	        ErrorLog("database,delete, %s"%e)
        cursor.close()
        db.close()
        return userid


#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def DeleteS(sql):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        userid=-1
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except Exception,e:
        	db.rollback()
	        ErrorLog("database,deletes, %s"%e)
        cursor.close()
        db.close()
        return userid


#----------------------------------------------------------------------------------------------
#--------------------------------------------------
def QueryS(sql):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        userid=-1
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except Exception,e:
		db.rollback()
                ErrorLog("database,query, %s"%e)
        cursor.close()
        db.close()
        return userid

