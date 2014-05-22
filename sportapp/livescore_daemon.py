#!/usr/bin/python
import time
from daemon import runner
import MySQLdb
import json
import urllib2
import base64
from utility import *

#sport api url
url_api="http://sports.espn.go.com/%s/bottomline/scores"
filepath="/media/hd2/sportapp/livescore.txt"
class App():
        def __init__(self):
                self.stdin_path = '/dev/null'
                self.stdout_path = '/dev/tty'
                self.stderr_path = '/dev/tty'
                self.pidfile_path =  '/tmp/foo.pid'
                self.pidfile_timeout = 5

        def run(self):
                while True:
                        #f=open('/var/www/sportapp/livescore.txt','w')
                        #f.write("")
                        #f.close()
                        self.SaveLive()
                        time.sleep(60*4)

        #get the news for all the sports
        def SaveLive(self):
		dicty={}
		for league in ['NFL', 'MLB', 'NBA', 'NHL','soccerspain','soccerportugal','soccernetherlands','soccerfrance','soccerchampions','soccereurope','soccergermany''socceritaly','soccerengland']:
			dicty[league]=league+" "+league#self.GetLivefeed(league)
		dicty2={}
		dicty2['sports']=dicty
		print json.dumps(dicty2)
		WriteXmlF(filepath,dicty)

	#----------------------------------------------------------------------------------------------
	#----------
	def GetSoccer(self,league):
  		d=urllib2.urlopen("http://www.goalserve.com/rss").read()
  		o = xmltodict.parse(d.replace('[','').replace(']','').replace('Status: ',''))
  		scoreA= (o['rss']['channel']['item'])
  		resultA=[]
  		for score in scoreA:
    			stringScore=''
    			if league=='soccerspain' and 'Spain' in score['title']:
      				stringScore=score['title']+"("+score['pubDate']+")"
    			elif league=='soccerengland'and 'England: Premier League' in score['title']:
      				stringScore=score['title'].replace(' - England: Premier League','')#+"("+score['pubDate']+")"
    			elif league=='socceritaly'and'Italy: Serie A' in score['title']:
      				stringScore=score['title'].replace(' - Italy: Serie A','')#+"("+score['pubDate']+")"
    			elif league=='soccergermany' and 'Germany: Bundesliga' in score['title']:
      				stringScore=score['title'].replace(' - Germany: Bundesliga','')#+"("+score['pubDate']+")"      
    			elif league=='soccerportugal' and 'Portugal: Portuguese Liga' in score['title']:
      				stringScore=score['title']#+"("+score['pubDate']+")" 
    			elif league=='soccernetherlands' and 'Netherlands: Eerste Divisie' in score['title']:
      				stringScore=score['title']#+"("+score['pubDate']+")"
    			elif league=='soccerfrance' and 'France: Ligue 1' in score['title']:
      				stringScore=score['title']
    			elif league=='soccerchampions' and 'Champions' in score['title']:
      				stringScore=score['title']#+"("+score['pubDate']+")"
    			elif league=='soccereurope' and 'Europe' in score['title']:
      				stringScore=score['title']#+"("+score['pubDate']+")"
    			if stringScore!='':resultA.append(stringScore)
 		dicty={}
  		dicty[KEY_RESULT]=resultA
  		dicty[KEY_ESIT]=ESIT_OK
  		return dicty

	#----------------------------------------------------------------------------------------------
	#----------
	def GetLiveFeed(self,league):
		if 'soccer' in league: return self.GetSoccer(league)
  		dicty={}
  		try:
    			unparsed=urllib2.urlopen(url_api%(league)).read()
    			token=unparsed.split('&')
    			timestamp = token[2]
    			timestamp = timestamp.split('=')[1]
    			tokenclean=[]
    			for i in token:
      				if '_s_left' in i:
        				i=i.split('=')[1]
        				i=i.replace("%20"," ")
        			tokenclean.append(i)
    			dicty[KEY_RESULT]=tokenclean
    			dicty[KEY_ESIT]=ESIT_OK
    			try:
      				dicty['timestamp']=int(timestamp)
    			except Exception, e:
      				ErrorLog("file livescore,def GetLiveFeed,exception:%s ,league:%s"%(e,league))
      				dicty['timestamp']=timestamp
    			return dicty
  		except Exception, e:
    			dicty[KEY_RESULT]="%s"%e
    			dicty[KEY_ESIT]=ESIT_ERROR
    			ErrorLog("file livescore,def GetLiveFeed,exception:%s ,league:%s"%(e,league))
	    		return dicty

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

#Note that you'll need the python-deaemon library. In Ubuntu, you would:
#sudo apt-get install python-daemon
#Then just start it with ./howdy.py start, and stop it with ./howdy.py stop.                                                              
