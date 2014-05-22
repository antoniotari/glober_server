#!/usr/bin/python
import urllib2
import urllib

def ErrorLog(message,typeS='generic'):
	d=urllib2.urlopen("http://162.216.4.195:8080/Glober3/api?cmd=errorlog&error=%s&message=%s"%(urllib.quote(message),urllib.quote(typeS))).read()
