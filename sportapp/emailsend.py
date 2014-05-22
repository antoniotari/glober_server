#!/usr/bin/python
import smtplib

def createhtmlmail (html, text, subject, fromEmail):
	"""Create a mime-message that will render HTML in popular
    	MUAs, text in better ones"""
    	import MimeWriter
    	import mimetools
    	import cStringIO

    	out = cStringIO.StringIO() # output buffer for our message 
    	htmlin = cStringIO.StringIO(html)
    	txtin = cStringIO.StringIO(text)

    	writer = MimeWriter.MimeWriter(out)
    	#
    	# set up some basic headers... we put subject here
    	# because smtplib.sendmail expects it to be in the
    	# message body
    	#
    	writer.addheader("From", fromEmail)
    	writer.addheader("Subject", subject)
    	writer.addheader("MIME-Version", "1.0")
    	#
    # start the multipart section of the message
    # multipart/alternative seems to work better
    # on some MUAs than multipart/mixed
    #
    	writer.startmultipartbody("alternative")
    	writer.flushheaders()
    #
    # the plain text section
    #
    	subpart = writer.nextpart()
    	subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
    	pout = subpart.startbody("text/plain", [("charset", 'us-ascii')])
    	mimetools.encode(txtin, pout, 'quoted-printable')
    	txtin.close()
    #
    # start the html subpart of the message
    #
    	subpart = writer.nextpart()
    	subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
    #
    # returns us a file-ish object we can write to
    #
    	pout = subpart.startbody("text/html", [("charset", 'us-ascii')])
    	mimetools.encode(htmlin, pout, 'quoted-printable')
    	htmlin.close()
    #
    # Now that we're done, close our writer and
    # return the message body
    #
    	writer.lastpart()
	msg = out.getvalue()
    	out.close()
    	#print msg
   	return msg

def sendemail(email):
	username = 'register@ocdsportsfan.com'
	password = 'Tsunami100'
    	html = '<a href="http://162.216.4.195/cgi-bin/sportapp/confirmemail.py?email=%s">Click here if you didn\'t create an OCD Sports Fan account using this email address</a><br><br>'%email
    	text = 'Let us know if you didn\'t create an OCD Sports Fan account using this email address'
    	subject = "Registration Confirm"
    	message = createhtmlmail(html, text, subject, 'OCD Sports Fan <register@ocdsportsfan.com>')
    	server = smtplib.SMTP("smtpout.secureserver.net",80)
    	server.ehlo()
	server.login(username, password)
    	server.sendmail('register@ocdsportsfan.com', [email], message)
    	server.quit()

if __name__=="__main__":
	sendemail()

def oldsendmail():
	print "Content-type:application/json\r\n\r\n"

	fromaddr = 'register@ocdsportsfan.com'
	toaddrs  = 'antoniotari11@gmail.com'
	msg = "<html><body>Click</body></html>"
	SUBJECT = 'OCD Sports Fan Email comfirmation'

	Html = """<p>Hi!<br>How are you?<br>Here is the <a href="http://www.python.org">link</a> you wanted.</p>"""

# Credentials (if needed)
	username = 'register@ocdsportsfan.com'
	password = 'Tsunami100'

# The actual mail send
	mailServer = smtplib.SMTP('smtpout.secureserver.net',80)#587)
#mailServer.ehlo()
#mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(username,password)

	BODY = '\r\n'.join(['To: %s' % toaddrs,
        	            'From: %s' % fromaddr,
                	    'Subject: %s' % SUBJECT,
                    	'', msg])

	try:
    		mailServer.sendmail(fromaddr, [toaddrs], BODY)
    		print ('email sent')
	except:
    		print ('error sending mail')

	mailServer.quit()

#server.sendmail(fromaddr, toaddrs, msg)
#server.quit()
