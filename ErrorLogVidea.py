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
	messag="%s %s %s"%(form.getvalue('error'),form.getvalue('deviceid'),form.getvalue('devicemanufacture'))
        sql = "INSERT INTO errorlog (appname,message,devicedate,ipaddress,ipaddressv6,deviceid,devicemanufacture,deviceModel,deviceSystemVersion,deviceType,deviceUniqueId,macaddress)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(form.getvalue('appname'),form.getvalue('error'),form.getvalue('date'),form.getvalue('ipaddress'),form.getvalue('ipaddressv6'),form.getvalue('deviceid'),form.getvalue('devicemanufacture'),form.getvalue('deviceModel'),form.getvalue('deviceSystemVersion'),form.getvalue('deviceType'),form.getvalue('deviceUniqueId'),form.getvalue('macaddress'))

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

