#!/usr/bin/python
import MySQLdb

import urllib2
import urllib
import json
import cgi
import cgitb
from defs import *
from database import SelectS,QueryS,existsS


print "Content-type:application/json\r\n\r\n"

try:
	form=cgi.FieldStorage()
        sql = "INSERT INTO savemessage (user,message,sender)VALUES('%s','%s','%s');"%(form.getvalue('user'),form.getvalue('message'),form.getvalue('sender'))

	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db="aterrorlog", use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        userid=-1
        try:
                cursor.execute(sql)
                userid=db.insert_id()
                db.commit()
        except Exception,e:
                db.rollback()
                print "database,query, %s"%e
        cursor.close()
        db.close()
        print userid

except Exception,e:
	print "%s"%e 
#def ErrorLog(message,typeS='generic'):
#        d=urllib2.urlopen("http://162.216.4.195:8080/Glober3/api?cmd=errorlog&error=%s&message=%s"%(urllib.quote(message),urllib.quote(typeS))).read()

