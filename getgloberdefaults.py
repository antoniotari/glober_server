#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmltodict, json
import cgi
import cgitb
import hashlib
import base64
import random
import ErrorLog

FILE_DEFAULTS_URL=	'/media/hd2/glober/appfiles/globerdefaults.xml'
SECURE_STRING_1=     "GERTYRJdffwjehrERERdfsdwtwerw3464674345gWINTER"
SECURE_STRING_2=     "GTRYSDF4534534535fgeryertyesdwtwegfgeyewrtGFGDFH4545g64674345gWINTER"


KEY_ESIT=       'esit'
KEY_RESULT=     'result'
KEY_CMD=        'cmd'
#----------------------------------------------------------------------------

#--------------------------------------------------------------------
#-----run the appropriate function for the received command
def HandleCommand():
	form=cgi.FieldStorage()
        cmd= form.getvalue(KEY_CMD)
        if cmd=='get_defaultvalues':
        	print GetDefaultValues(form)
        elif cmd=='get_defaultvalues_secure':
                print GetDefaultValues(form,True)
	elif cmd==None:
		print GetDefaultValues(form,True)
	elif cmd=='test1':
                print 'test1'
        else:
                print 'error command unknown'

def GetDefaultValues(form,secure=False):
	if secure:
		if Authenticate(form)==False: return

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
                
                #print xmlS
                o = xmltodict.parse(xmlS)
                dicty={}
		returnD={}
		try:	
			dicty['glober_appname']=o['returnvalue']['result']['glober_appname']
                        dicty['glober_apple_appid']=o['returnvalue']['result']['glober_apple_appid']
                        dicty['glober_facebook_appkey']=o['returnvalue']['result']['glober_facebook_appkey']
                        dicty['glober_secure']=o['returnvalue']['result']['glober_secure']
                        dicty['glober_url_api_secure']=o['returnvalue']['result']['glober_url_api_secure']
                        dicty['glober_url_api']=o['returnvalue']['result']['glober_url_api']
			dicty['glober_url_picturebase']=o['returnvalue']['result']['glober_url_picturebase']
                        dicty['glober_url_bridgeget']=o['returnvalue']['result']['glober_url_bridgeget']                        
			dicty['glober_url_bridgepost']=o['returnvalue']['result']['glober_url_bridgepost']
			dicty['glober_key_bridgepost']=o['returnvalue']['result']['glober_key_bridgepost']
			dicty['glober_value_bridgepost']=o['returnvalue']['result']['glober_value_bridgepost']
                        dicty['glober_keyurl_bridgepost']=o['returnvalue']['result']['glober_keyurl_bridgepost']
                        dicty['google_apikey']=o['returnvalue']['result']['google_apikey']
                        dicty['glober_introvideo_url']=o['returnvalue']['result']['glober_introvideo_url']
                        dicty['glober_googleanalytics_trackid']=o['returnvalue']['result']['glober_googleanalytics_trackid']
                        dicty['glober_googleanalytics_interval']=o['returnvalue']['result']['glober_googleanalytics_interval']
                        dicty['glober_pinginterval']=o['returnvalue']['result']['glober_pinginterval']
                        dicty['glober_apigee_appid']=o['returnvalue']['result']['glober_apigee_appid']
                        dicty['glober_apigee_consumerkey']=o['returnvalue']['result']['glober_apigee_consumerkey']
                        dicty['glober_apigee_secret']=o['returnvalue']['result']['glober_apigee_secret']
                        dicty['glober_map_milesrange']=o['returnvalue']['result']['glober_map_milesrange']
                        dicty['glober_loadlocalbusiness']=o['returnvalue']['result']['glober_loadlocalbusiness']
                        dicty['glober_admobactive']=o['returnvalue']['result']['glober_admobactive']
                        dicty['glober_stoppingonexit']=o['returnvalue']['result']['glober_stoppingonexit']
                        dicty['glober_googleanalyticsactive']=o['returnvalue']['result']['glober_googleanalyticsactive']
                        dicty['glober_apigeeactive']=o['returnvalue']['result']['glober_apigeeactive']
                        dicty['glober_resetdefaults']=o['returnvalue']['result']['glober_resetdefaults']
                        dicty['glober_startdelayedping']=o['returnvalue']['result']['glober_startdelayedping']
                        dicty['enableinapp']=False
			dicty['enableverifyreceiptinapp']=True
		except Exception, defe:
			returnD['anyerror']="%s"%defe	
			ErrorLog.ErrorLog("%s"%defe,"user.getdefaults_python")
                returnD[KEY_ESIT]=0
		if secure:
			result64=base64.b64encode(json.dumps(dicty))
			posAdd=random.randrange(11,len(result64)-11)
			result64D={}
			result64D['hash'] = result64[:posAdd] + 'ejkffgkjfgsjhdfgsAntsdsdfTarffgkz' + result64[posAdd:]
			returnD[KEY_RESULT]=result64D
		else:
			returnD[KEY_RESULT]=dicty#o['returnvalue']
		return json.dumps(returnD)
        except Exception, defe2:
		ErrorLog.ErrorLog("outer exception %s"%defe2,"user.getdefaults_python")
                de={}
                de[KEY_ESIT]=-1
                de[KEY_RESULT]='error main() exception'
                return json.dumps(de)

#--------------------------------------------------------------------
#-----SECURITY FUNCTION AUTHENTICATION
def Authenticate(form):

	secdeviceid=form.getvalue('broccolidevuid')
        sectoken=form.getvalue('broccolitoken')
        secsync=form.getvalue('broccolisync')

        if(sectoken==None):return False
        if(secdeviceid==None):return False
        if(secsync==None):return False
        if(len(secdeviceid)<11): return False

        mdS =  "%s%s%s%s"%(secdeviceid,SECURE_STRING_1,secsync,SECURE_STRING_2)

        m = hashlib.md5()
        m.update(mdS)
        criptedS= m.hexdigest()
        if criptedS==sectoken: return True
        return False


def main():
        print "Content-type:application/json\r\n\r\n"
        HandleCommand()

#----------------------------------------------------------------------------
#-----START the script

if __name__ == '__main__':
    main()

#----------------------------------------------------------------------------
