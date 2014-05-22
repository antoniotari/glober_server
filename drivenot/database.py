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

#----------------------------------------------------------------------------------------------
#----------check if an element into the table exists
def exists(table,key,value):
	db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
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
def exists(table,hashMap):
	#form the sql statement
	whereStat=' WHERE '
	for key, value in hashMap.iteritems():
		whereStat=whereStat+key+"='"+value+"' AND "
	sql="SELECT count(*) as total FROM "+table+whereStat[:-5]+";"
	db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
	cursor=db.cursor(MySQLdb.cursors.DictCursor)
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
#----------get the value from the table where key=value
def getValue(table,keyToGet,key,value):
        db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
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
#----------get the value from the table where key=value
def getValue(table,keyToGet,hashMap):
        db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
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
        db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
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
        return userid

