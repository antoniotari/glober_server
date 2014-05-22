#!/usr/bin/python
import MySQLdb
import json
import base64
import random
import string
import urllib2
import cgi
import cgitb
import datetime
import time
import xmltodict
import os.path

from defs import FILE_DEFAULTS_URL

ERRORLOG_PATH='/media/hd2/sportapp/sportapp_log.txt'

#--------------------------------------------------------------------
#-----getDefaults
def getDefaults():
        try:
                f = open(FILE_DEFAULTS_URL,'r')
                i=0;
                xmlS=''
                for line in f:
                        if(i>0):
                                xmlS=xmlS+line
                        i=i+1
                #lines = f.readlines()
                f.close()
                return  (xmltodict.parse(xmlS))['returnvalue']['result']
        except:
                return None 

#--------------------------------------------------------------------
#-----
def getAdminUid():
	dicty=getDefaults()
	if dicty==None: return ""
	return "%s"%dicty['sportapp_adminuser_uid']

#--------------------------------------------------------------------
#-----clean the string to put in the database
def encodedb(value):
	return value.replace("'","\\\'").replace("\"","\\\"").replace("(","[").replace(")","]")

#--------------------------------------------------------------------
#-----check if the variable is string, if not turn it into a string
def strize(s):
	if isinstance(s, basestring)==False:
		return "%s"%s
	return s

#--------------------------------------------------------------------
#-----open a xml file and return a dictionary
def ReadXmlF(filepath):
	try:
		#f=None
                #if os.path.exists(filepath) and os.path.isfile(filepath):
		f = open(filepath,'r')
                #else: return None
		i=0;
                xmlS=''
                for line in f:
                        if(i>0):
                                xmlS=xmlS+line
                        i=i+1
                #lines = f.readlines()
                f.close()

                #print xmlS
                return xmltodict.parse(xmlS)
        except Exception,e:
		ErrorLog("readxmlfile, error:%s"%e)
		return None

#--------------------------------------------------------------------
#-----write a dictionary into a xml file
def WriteXmlF(filepath,dicty):
	try:
		cool=xmltodict.unparse(dicty)
		f=open(filepath,'w')
                f.write(cool)
                f.close()
		return True
	except Exception,e:
                ErrorLog("file utility,def writexmlfile, error:%s"%e)
                return False

#--------------------------------------------------------------------
#-----add element to xml file
def PutXmlF(filepath,key,value):
	dicty={}
	if os.path.exists(filepath) and os.path.isfile(filepath):
		dicty=ReadXmlF(filepath)
	dicty[key]=value
	return WriteXmlF(filepath,dicty)

#--------------------------------------------------------------------
#-----extract the hash tag from a string
def ErrorLog(errormessage):
	er=''
	try:
		f=open(ERRORLOG_PATH,'a')
		dicty={}
		dicty['date']="%s"%datetime.datetime.now()
		dicty['error']="%s"%errormessage
		f.write(json.dumps(dicty)+"\n")
		#f.write("date:%s\n%s\n\n"%(datetime.datetime.now(),"%s"%errormessage))
		f.close()	
	except Exception,g:
		er='1'

#--------------------------------------------------------------------
#-----extract the hash tag from a string
def ExtractHashTags(s):
	return set(part[1:] for part in s.split() if part.startswith('#'))

#--------------------------------------------------------------------
#-----
def DateToLong(queryAr):
	if type(queryAr) is dict:
		return checkIfDate(queryAr)
	elif is_array(queryAr):
		resultAr=[]
		for row in queryAr:
		#for key in row:
		#	if isinstance(row[key],datetime.date): row[key]=TimeUtc(row[key])
			resultAr.append(checkIfDate(row))
		return resultAr
	elif isinstance(queryAr,datetime.date): 
		return TimeUtc(queryAr)
	return queryAr

def checkIfDate(row):
	for key in row:
        	if isinstance(row[key],datetime.date): row[key]=TimeUtc(row[key])
        return row

def is_array(var):
	return isinstance(var, (list, tuple))
    	#return isinstance(var, list)
#--------------------------------------------------------------------
#-----
def RemoveKey(queryAr,key):
	if type(queryAr) is dict:
		if key in queryAr: del queryAr[key]
		return queryAr
	elif is_array(queryAr):
		resultAr=[]
		for dicti in queryAr:
			if key in dicti: del dicti[key]
			resultAr.append(dicti)
        	return resultAr
	return queryAr
#--------------------------------------------------------------------
#-----
def RemovePassword(queryAr):
	return RemoveKey(queryAr,'password')

#--------------------------------------------------------------------
#-----it generates a random string, useful for filenames
def TimeUtc(timeD):
	if timeD==None: return 0.0
	return time.mktime(timeD.timetuple())

#--------------------------------------------------------------------
#-----it generates a random string, useful for filenames
def id_generator(size=22, chars=string.ascii_uppercase + string.digits):
	dnow=TimeUtc(datetime.datetime.now())
	drand= ''.join(random.choice(chars) for x in range(size))
	return "%s%d"%(drand,dnow)
#--------------------------------------------------------------------
#-----returns the json string from the fetched array
def RetJson(cursor):
	results=cursor.fetchall()
        desc=cursor.description
        i=0
        resultA=[]
        for row in results:
        	d={}
                i=0
                for row2 in row:
                	d[row2]="%s"%(row[row2])
                        i=i+1
                resultA.append(d)
        return resultA

#--------------------------------------------------------------------
#-----
def UrlDecode(thestring):
	return urllib2.unquote(thestring.decode('utf8'))

#--------------------------------------------------------------------
#-----
def hvalue(form,key):
	tempV=form.getvalue(key)
	if(tempV==None):return None
	return UrlDecode(form.getvalue(key))
