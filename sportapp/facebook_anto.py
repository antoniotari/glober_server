#!/usr/bin/python
import json
import base64
import random
import string
import facebook
from database import *
from utility import ErrorLog
from login import SaveToken,FB_GRAPH_URL
import urllib2
import urllib

app_id = "539509902792319"
app_secret = "3db494cfd35e2d7ca40609da01cacab3"
message ='defined%20message'
data='defined%20data'

def PostWall(fbtoken,useruid,messageS):
	dicty={}
	try:
		graph = facebook.GraphAPI(fbtoken)
		#profile = graph.get_object("me")
		#friends = graph.get_connections("me", "friends")
		dicty[KEY_RESULT]=graph.put_object("me", "feed", message=messageS)
		dicty[KEY_ESIT]=ESIT_OK
	except Exception,e:
                ErrorLog("getpostfromid , error:%s"%e)
                dicty[KEY_RESULT]="%s"%e
                dicty[KEY_ESIT]=ESIT_ERROR
        return dicty


def AppRequest(user_id):
	#token_url = "https://graph.facebook.com/oauth/access_token?"+"client_id=" + app_id +"&client_secret=" + app_secret +"&grant_type=client_credentials"
	token_url="https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials"%(app_id,app_secret)
	app_access_token=urllib2.urlopen(token_url).read()
	apprequest_url ="https://graph.facebook.com/%s/apprequests?message='%s'&data='%s'&%s&method=post"%(user_id,message,data,app_access_token)
	result=urllib2.urlopen(apprequest_url).read()
	return json.loads(result)
	

def GetFriends(token,userid):
	#try:
	#	graph = facebook.GraphAPI(token)
	#	friends = graph.get_connections("me", "friends")
	#except:
	#	ErrorLog('file facebook_anto, def GetFriends, try 0.5 , invalid token?')
	#	return -1
	
	#get complete list of facebook friends
	try:
		friends=json.loads(urllib2.urlopen(FB_GRAPH_URL+"me/friends?fields=name,first_name,gender,address,email,location,username,last_name,picture&access_token="+token).read())	
	except:
                ErrorLog('file facebook_anto, def GetFriends, try 0, invalid token?')
                return -1

	try:
                SaveToken(userid,token)
        except:
                ErrorLog('file facebook_anto, def GetFriends, try 0.5')

	#insert all the friends into the facebook_friends table
	tablefriends='facebook_friends'
	friendsA=[]
	try:
		friendsA=friends['data']
		for row in friendsA:
			#check if the user_uid-friend_fbid exists
			mapex={}
			mapex['user_uid']=userid
			mapex['friend_fbid']="%s"%row['id']
			if (exists(tablefriends,mapex))==False:
				mapex['friend_fbid']="%s"%row['id']
				if 'name' in row: mapex['friend_fbname']=row['name']
				if 'username' in row: mapex['fbusername']=row['username']
				if 'first_name' in row: mapex['fbfirstname']=row['first_name']
				if 'last_name' in row: mapex['fblastname']=row['last_name']
				if 'gender' in row: mapex['fbgender']=row['gender']	
				try:
					mapex['fbpicture']=row['picture']['data']['url']
				except:
					ErrorLog('file facebook_anto, def GetFriends, try 0.7 , cant save friend facebook pic')
				Insert(tablefriends,mapex)
			#if the user is a sportapp user add his 
			try:
				checkIfAlreadyUser("%s"%row['id'])
			except:
				ErrorLog('file facebook_anto, def GetFriends, try 2')	
	except:
		ErrorLog('file facebook_anto, def GetFriends, try 1') 
	return friendsA

#----
#if the user is a sportapp user add his uid on all the records
def checkIfAlreadyUser(fbid):
	mapex={}
        mapex['fbid']=fbid
        if (exists('user',mapex))==True:
		QueryS("UPDATE facebook_friends SET friend_user_uid='%s' WHERE friend_fbid='%s';"%(getValueS('user','uid','fbid',fbid),fbid))
#---
#replaced by login.SaveToken
def updateFbToken(uid,fbt):
	if existsS('accesstoken','user_uid',uid)==False:
		mapI={}
                mapI['accesstoken']=fbt
                mapI['user_uid']=uid
                Insert('accesstoken',mapI)
	else:
		mapex={}
                mapex['user_uid']=uid
                mapex['accesstoken']=fbt
		if exists('accesstoken',mapex)==False:
			QueryS("UPDATE accesstoken SET accesstoken='%s' WHERE user_uid='%s';"%(fbt,uid))

		
