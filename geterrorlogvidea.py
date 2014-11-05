#!/usr/bin/python
import MySQLdb

import urllib2
import urllib
import json
import cgi
import cgitb
from defs import *
from database import SelectS,QueryS,existsS
from utility import DateToLong

print "Content-type:application/json\r\n\r\n"

try:
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db="aterrorlog", use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        resultA=[]
        dicty={}
	try:
                queryEsit=cursor.execute("SELECT * FROM errorlog WHERE appname='%s' ORDER BY serverdate DESC;"%"Videa")
                resultA=DateToLong(cursor.fetchall())
        except Exception,e:
                #print "database,selectS, %s"%e
                resultA=[]
        cursor.close()
        db.close()
        dicty["values"]=resultA
	print json.dumps(dicty)

except Exception,e:
	print "%s"%e 
#def ErrorLog(message,typeS='generic'):
#        d=urllib2.urlopen("http://162.216.4.195:8080/Glober3/api?cmd=errorlog&error=%s&message=%s"%(urllib.quote(message),urllib.quote(typeS))).read()

