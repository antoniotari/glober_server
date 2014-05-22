#!/usr/bin/python
import cgi
import cgitb
import json
from py4j.java_gateway import JavaGateway, GatewayClient

print "Content-type:application/json\r\n\r\n"
form=cgi.FieldStorage()
lati=form.getvalue("latitude")
longi=form.getvalue("longitude")
gateway = JavaGateway(GatewayClient(port=30581))
responseS=gateway.entry_point.GetBusinessS(float("%s"%lati),float("%s"%longi))
d=json.loads(responseS)
responseJ={}
#try:
#	d=json.loads(responseS)
#except:
#	d=responseS

responseJ['esit']=0
responseJ['result']=d
print json.dumps(responseJ)
