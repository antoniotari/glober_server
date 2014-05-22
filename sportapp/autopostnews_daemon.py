#!/usr/bin/python
import time
from daemon import runner
import MySQLdb
import json
import urllib2
import urllib
import base64
from utility import *
from defs import *
from wall import PostOnWall
from notification import InsertNotification
import pictures
import push
import user
import database
from dateutil import parser

ESPN_APIKEY=    'ufuancvzf7xb58f9zh7khr32'
ESPN_BASEURL=   'http://api.espn.com/v1/'

#sport api url
class App():
        def __init__(self):
                self.stdin_path = '/dev/null'
                self.stdout_path = '/dev/tty'
                self.stderr_path = '/dev/tty'
                self.pidfile_path =  '/tmp/foo2.pid'
                self.pidfile_timeout = 5

	def run(self):
		while True:			
			self.ReadNews('baseball')
			self.ReadNews('hockey')
			self.ReadNews('soccer')
			self.ReadNews('basketball')
			self.ReadNews('football')
			time.sleep(60*60*2)

	
	def ReadNews(self,sport):
                baseballD={}
        	try:
                        baseballJ=urllib2.urlopen(ESPN_BASEURL+"sports/%s/news/headlines/?apikey=%s"%(sport,ESPN_APIKEY)).read()
                        baseballD = json.loads(u''+baseballJ)
                        baseballA = baseballD['headlines']
                        resultCount=baseballD['resultsCount']
                        counter=baseballD['resultsOffset']
                        limit=baseballD['resultsLimit']
                        counter=counter+limit
                        
			while(counter<resultCount):
                                time.sleep(3)
                                baseballJ=urllib2.urlopen(ESPN_BASEURL+"sports/%s/news?apikey=%s&offset=%d"%(sport,ESPN_APIKEY,counter)).read()
                                baseballA2 = json.loads(u''+baseballJ)['headlines']
                                for row in baseballA2:
                                        baseballA.append(row)
                                counter=counter+limit
                        time.sleep(3)
			baseballD['headlines']=baseballA
			counteri=0
			for singleNews in baseballA:
                        	try:
					newsTitle=''
                                        #try:
                                        #       newsDesc=singleNews['description']
                                        #except Exception,r:
                                        #       ErrorLog("post daemon, no description? exception r: %s\nthe news:%s"%(r,json.dumps(singleNews)))
                                        #       newsDesc=''
                                        if 'title' in singleNews:
                                                newsTitle=singleNews['title']
                                        elif 'headline' in singleNews:
                                                newsTitle=singleNews['headline']

                                	image64=None
                                        if 'images' in singleNews:
						imagesD=singleNews['images']
                                        	try:
							if len(singleNews['images'])>0:
								url=singleNews['images'][0]['url']
                                                		image64=pictures.Base64FromUrl(url)
						except Exception ,ll:
							ErrorLog("post daemon, getting imange exception: %s \nimages dict %s"%(ll,json.dumps(imagesD)))
                                	descr='#%s'%sport	
					if 'categories' in singleNews:
						catA=singleNews['categories']
						for catD in catA:
							if 'description' in catD:
								dt = parser.parse(singleNews['published'])
								difTime=time.time() - time.mktime(dt.timetuple())
								if difTime<60*60*2 :
									linknp=''
									try:
										linknp=singleNews['links']['mobile']['href']	
									except:
										linknp=''
									self.SendPushTag((catD['description']).replace(" ","").replace(".","").replace("'",""),newsTitle,linknp)
								descr='#'+(catD['description']).replace(" ","").replace(".","").replace("'","")+' '+descr
					counteri=counteri+1
					newsDesc=''
					if 'description' in singleNews:newsDesc=singleNews['description']
					#sometimes (ie.for score results) title and description are the same
					if newsTitle==newsDesc:newsDesc=''					

					postD=PostOnWall(getAdminUid(),"%s<br>%s<br>%s"%(descr,newsTitle,newsDesc),None,image64,None,True,singleNews['id'],singleNews['published'])
					if postD==None:
						postD={}
						postD[KEY_RESULT]=database.getValueS('wall','id','newsid',"%s"%singleNews['id'])
					#extract the news link
                                        try:
						if 'links' in singleNews:
                                                	if 'mobile' in singleNews['links']:
                                                        	database.QueryS("INSERT IGNORE INTO newslinks (wall_id,link) VALUES ('%s','%s')"%(postD[KEY_RESULT],singleNews['links']['mobile']['href']))
                           		except Exception,linkex:
						ErrorLog("post daemon, inner exception linkex: %s"%linkex)
				except Exception,f:
                              		ErrorLog("post daemon, inner exception f: %s"%f)
			#baseballD['totalcount']=len(baseballA)
		except:
                        baseballD={}
       		#return baseballD

	def SendPushTag(self,desc,message,link=''):
		try:
			users=database.SelectS("SELECT uid from user")
			for singleUser in users:
				teams=user.ReturnUserTeams("%s"%singleUser['uid'])
				for team in teams:
					teamPars=(team['name']).replace(" ","").replace(".","").replace("'","").lower()
					if (desc.lower() in teamPars) or(teamPars in desc.lower()):
						#generate the notification
						try:
							notifmess={}
							notifmess['message']=message
							notifmess['link']=link
							messageNot=json.dumps(notifmess)			
							InsertNotification(messageNot,NOTIF_TYPENEWS,'0',getAdminUid(),"%s"%singleUser['uid'])
						except Exception,noex:
							ErrorLog("post daemon,cant insert notification SendPushTag :%s"%noex)
						ErrorLog(push.SendPush("",getAdminUid(),"%s"%singleUser['uid'],"m",message))
		except Exception,exc:
			ErrorLog("post daemon,SendPushTag: %s"%exc)

	def ReadNews_old(self):
		try:
			newsPostA=[]
			#resA= json.loads(urllib2.urlopen("http://localhost/sportapp/teamnews.txt").read())[KEY_RESULT]
			for singleSport in resA:
				resB=singleSport['headlines']
				for singleNews in resB:
					try:
						image64=None
						if 'images' in singleNews:
							url=singleNews['images'][0]['url']
							image64=pictures.Base64FromUrl(url)
						PostOnWall(getAdminUid(),"%s\n\n%s"%(singleNews['title'],singleNews['description']),None,image64,None,True,singleNews['id'],singleNews['published'])
					except Exception,f:
						ErrorLog("post daemon, inner exception f: %s"%f)
		except Exception , m:
			ErrorLog("post daemon, outer exception m: %s"%m)
			return None		

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

#Note that you'll need the python-deaemon library. In Ubuntu, you would:
#sudo apt-get install python-daemon
#Then just start it with ./howdy.py start, and stop it with ./howdy.py stop.

