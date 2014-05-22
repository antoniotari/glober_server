#!/usr/bin/python
import MySQLdb
import json
import urllib2
import urllib
from defs import *

offs=250
teams=json.loads(urllib2.urlopen("http://api.espn.com/v1/sports/football/college-football/teams?apikey=ufuancvzf7xb58f9zh7khr32&offset=%d"%offs).read())['sports'][0]['leagues'][0]['teams']
ii=0
for team in teams:
		db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
		cursor=db.cursor(MySQLdb.cursors.DictCursor)
		try:
			ii=ii+1
			kk=cursor.execute("INSERT INTO team (league_espn_id,isTournament,country_name,country_abbreviation,team_id,team_uid,location,name,nickname,abbreviation,color,link_api_teams,link_api_news,link_api_notes,link_web_teams,link_mobile_teams)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%('23','0','USA','USA',team['id'],team['uid'],team['location'],team['name'],team['nickname'],team['abbreviation'],team['color'],team['links']['api']['teams']['href'],team['links']['api']['news']['href'],team['links']['api']['notes']['href'],team['links']['web']['teams']['href'],team['links']['mobile']['teams']['href']))
			db.commit()
			print ii 
		except Exception ,d:
			print "%s"%d
		cursor.close()
		db.close()
