#!/usr/bin/python
import pytz
import datetime
import time
import urllib2
import urllib
import json
import os
import xmltodict
import elementtree.ElementTree as ET
from utility import ErrorLog
from defs import *

# e.g. http://scores.nbcsports.msnbc.com/ticker/data/gamesMSNBC.js.asp?jsonp=true&sport=MLB&period=20120929
url = 'http://scores.nbcsports.msnbc.com/ticker/data/gamesMSNBC.js.asp?jsonp=true&sport=%s&period=%d'

#sport api url
url_api="http://sports.espn.go.com/%s/bottomline/scores"
#basket nba
#http://sports.espn.go.com/nba/bottomline/scores
#baseball mlb
#http://sports.espn.go.com/mlb/bottomline/scores
#hockey nhl
#http://sports.espn.go.com/nhl/bottomline/scores
#college football
#http://sports.espn.go.com/ncf/bottomline/scores
#football nfl
#http://sports.espn.go.com/nfl/bottomline/scores


#----------------------------------------------------------------------------------------------
#----------
def today(league):
  yyyymmdd = int(datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y%m%d"))
  games = []
  
  try:
    f = urllib2.urlopen(url % (league, yyyymmdd))
    jsonp = f.read()
    f.close()
    json_str = jsonp.replace('shsMSNBCTicker.loadGamesData(', '').replace(');', '')
    json_parsed = json.loads(json_str)
    for game_str in json_parsed.get('games', []):
      game_tree = ET.XML(game_str)
      visiting_tree = game_tree.find('visiting-team')
      home_tree = game_tree.find('home-team')
      gamestate_tree = game_tree.find('gamestate')
      home = home_tree.get('nickname')
      away = visiting_tree.get('nickname')
      os.environ['TZ'] = 'US/Eastern'
      start = int(time.mktime(time.strptime('%s %d' % (gamestate_tree.get('gametime'), yyyymmdd), '%I:%M %p %Y%m%d')))
      del os.environ['TZ']
      
      games.append({
        'league': league,
        'start': start,
        'home': home,
        'away': away,
        'home-score': home_tree.get('score'),
        'away-score': visiting_tree.get('score'),
        'status': gamestate_tree.get('status'),
        'clock': gamestate_tree.get('display_status1'),
        'clock-section': gamestate_tree.get('display_status2')
      })
  except Exception, e:
    print e
  
  return games


#----------------------------------------------------------------------------------------------
#----------
def GetSoccer(league):
  d=urllib2.urlopen("http://www.goalserve.com/rss").read()
  o = xmltodict.parse(d.replace('[','').replace(']','').replace('Status: ',''))
  scoreA= (o['rss']['channel']['item'])
  resultA=[]
  for score in scoreA:
    stringScore=''
    if league=='soccerspain' and 'Spain' in score['title']:
      stringScore=score['title']+"("+score['pubDate']+")"
      #resultA.append(stringScore)
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
def GetLiveFeed(league):
  if 'soccer' in league: return GetSoccer(league)
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
    

#----------------------------------------------------------------------------------------------
#----------
if __name__ == "__main__":
  for league in ['NFL', 'MLB', 'NBA', 'NHL','MLS']:
    print today(league)
    time.sleep(3)
