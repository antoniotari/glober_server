#!/usr/bin/python
import json
from py4j.java_gateway import JavaGateway, GatewayClient
from defs import *
from database import *
import MySQLdb
from utility import DateToLong


def GetLocations(lati,longi):
	gateway = JavaGateway(GatewayClient(port=30581))
	responseS=gateway.entry_point.GetBusinessS(float("%s"%lati),float("%s"%longi))
	d=json.loads(responseS)
	responseJ={}
	responseJ['esit']=ESIT_OK
	responseJ[KEY_RESULT]=d
	return SaveToDB(responseJ)
	#return responseJ


def SaveToDB(locationsJ):
	locationsA=locationsJ[KEY_RESULT]
	resultA=[]
	for location in locationsA:
		mapInsert={}
		#change the glober image with a new image
		if "http://162.216.4.195/love/img/businesspic/" in location['image']:location['image']="http://162.216.4.195/sex/default_businessimage.png"

		location['Description']=location['description']
	
		mapInsert['name']=location['name']
		mapInsert['latitude']="%.16f"%location['Latitude']
		mapInsert['longitude']="%.16f"%location['Longitude']
		mapInsert['zip']="%s"%location['zip']
                mapInsert['state']=location['state']
                mapInsert['address']=location['vicinity']
                mapInsert['image']=location['image']
                mapInsert['font']=location['font']
                mapInsert['idapi']="%s"%location['id']
                mapInsert['frame']=location['frame']                
		mapInsert['website']=location['website']                
		mapInsert['type']=location['businessType']                
		mapInsert['description']=location['description']		
		mapInsert['nationality']=location['nationality']		
		mapInsert['logo']=location['Logo']
		
	
		if Insert('business',mapInsert)!=-1 and mapInsert['longitude']!=0 and 'restaurant' not in mapInsert['description'] and 'food' not in mapInsert['description']:
			resultA.append(location)
	locationsJ[KEY_RESULT]= resultA
	return locationsJ

def GetBusinessFromDatabase(businessId):
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
        sql="SELECT * from business WHERE idapi='%s';"%(businessId)
	dicty={}
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                results=DateToLong(results)
		dicty=results[0] 
        except:
		dicty={}
	cursor.close()
	db.close()
	return dicty
