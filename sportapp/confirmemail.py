#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import database
import utility
#import emailsend
if __name__=="__main__":

	print "Content-type:text\r\n\r\n"
	try:
		form=cgi.FieldStorage()
		email="%s" % form.getvalue('email')
		database.QueryS("UPDATE user set active=0 WHERE email='%s'"%email)
		print "Email confirmed, you can now login using your email and password"
	except Exception , d:
		utility.ErrorLog("confirmemail.py  %s"%d)
