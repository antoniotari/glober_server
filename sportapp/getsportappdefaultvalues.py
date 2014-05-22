#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmltodict, json
import cgi
import cgitb
from defs import FILE_DEFAULTS_URL,KEY_ESIT,KEY_RESULT,KEY_CMD
import utility
#FILE_DEFAULTS_URL=	'/media/hd2/sportapp/sportappdefaults.xml'

#KEY_ESIT=       'esit'
#KEY_RESULT=     'result'
#KEY_CMD=        'cmd'
#----------------------------------------------------------------------------

#--------------------------------------------------------------------
#-----run the appropriate function for the received command
def HandleCommand():
	form=cgi.FieldStorage()
        cmd="%s" % form.getvalue(KEY_CMD)
        if cmd=='hhhgfjdlrtpefdlkjgkrpsjngmybestfriend':
        	print GetDefaultValues()
        elif cmd=='test1':
                print 'test1'
        else:
                print 'error command unknown'

def GetDefaultValues():
	returnD=utility.getDefaults()
	de={}
	if returnD==None:
                de[KEY_ESIT]=-1
                de[KEY_RESULT]='error defaults'
                return json.dumps(de)

	de[KEY_RESULT]=returnD
        de[KEY_ESIT]=0
        return json.dumps(de)

def GetDefaultValuesOld(form):
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
                returnD=o['returnvalue']
                returnD[KEY_ESIT]=0
                return json.dumps(returnD)
        except:
                de={}
                de[KEY_ESIT]=-1
                de[KEY_RESULT]='error main() exception'
                return json.dumps(de)

def main():
        print "Content-type:application/json\r\n\r\n"
        HandleCommand()

#----------------------------------------------------------------------------
#-----START the script

if __name__ == '__main__':
    main()

#----------------------------------------------------------------------------
