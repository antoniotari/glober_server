#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import json
import cgi
import cgitb
import base64
import random
import string
#import simplejson
from PIL import Image
from py4j.java_gateway import JavaGateway
import hashlib

#import the file with all the common constansts
from defs import *
from database import *
from utility import *
from login import *
from user import *
from teams import *
from checkin import *
from chat import *
from push import *
from location import *
from follow import *
from images import *
from wall import *
from notification import *
from taunt import *
import facebook_anto
import livescore
import like
import block

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
#-----BEGIN of the Api class
class Api:
        'api to access read write into the database'
        countI=0

        #--------------------------------------------------------------------
        #-----constructor
        def __init__(self):
                self.countI=self.countI+1

        #--------------------------------------------------------------------                   
        #-----destructor
        def __del__(self):
                try:
                        self.DBclose()
                        self.countI-=1
                except:
                        print ''

        #--------------------------------------------------------------------
        #-----
        def DB(self):
                #if db.open==0:
                #       db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
                return db

        #--------------------------------------------------------------------
        #-----  
	def DBclose(self):
                try:
                        if db.open:
                                db.close()
                except:
                        print ''
	
        #--------------------------------------------------------------------
        #-----run the appropriate function for the received command
        def HandleCommand(self):
                form=cgi.FieldStorage()
		#security check
		if self.Authenticate(form)==False :
                	dd={}
                	dd[KEY_ESIT]=ESIT_SECUTIRYFAULT
                	dd[KEY_RESULT]="security check failed"
                	print json.dumps(dd)
                	return
		
		cmd="%s" % form.getvalue(KEY_CMD)
		#ErrorLog("cmd %s"%cmd)
		returnJ={}
		if cmd==CMD_SENDPUSH:
		        returnJ=SendPush(form.getvalue('device'),form.getvalue('from'),form.getvalue('to'),form.getvalue('type'),form.getvalue('message'))
			#print self.SendPush(form)               
		else:
			if cmd=='test':
                        	returnJ= json.loads(self.TestConnection(form))
				#print json.dumps(returnJ)
                	elif cmd=='fbhash':
				try:
					ErrorLog("%s"%(hvalue(form,"hash")))
                        		#print self.SaveFbHash(form)
				except Exception ,l:
					ErrorLog("HASH EXCEPTION : %s"%l)
				return
			elif cmd==CMD_REGISTERDEVICE:
				#correction of a old bug:
				useruidtok=hvalue(form,'useruid')
				if useruidtok==None: useruidtok=hvalue(form,'userid')
				returnJ= RegisterToken(hvalue(form,'token'),hvalue(form,'type'),hvalue(form,'deviceid'),useruidtok,hvalue(form,'development'),hvalue(form,'version'))
			elif cmd==CMD_LOGINFB:
				returnJ= json.loads( self.LoginFB(form))
			elif cmd==CMD_GETUSERPIC:
				useruid=tokenfb="%s" % form.getvalue('useruid')
				returnDi={}
				image64=UserImage(useruid,False)	
				if image64 != '':
					returnDi[KEY_ESIT]=ESIT_OK
				else:
                                        returnDi[KEY_ESIT]=ESIT_ERROR
				returnDi[KEY_RESULT]=image64#UserImage(useruid,False)
				returnJ=returnDi
			elif cmd==CMD_GETUSERTHUMB:
                                useruid=tokenfb="%s" % form.getvalue('useruid')
                                returnDi={}
                                image64=UserImage(useruid,True)
				if image64 != '':
                                        returnDi[KEY_ESIT]=ESIT_OK
                                else:
                                        returnDi[KEY_ESIT]=ESIT_ERROR
                                returnDi[KEY_RESULT]=image64
				returnJ=returnDi
			elif cmd==CMD_GETUSERCOVER:
                                try:
                                #	returnDi={}
                                #	image64=UserImageCover(hvalue(form,'useruid'),False)
                                #	if image64 != '':
                                #       	returnDi[KEY_ESIT]=ESIT_OK
                                #	else:
                                #        	returnDi[KEY_ESIT]=ESIT_ERROR
                                #	returnDi[KEY_RESULT]=image64#UserImage(useruid,False)
                                #	returnDi['cover']=imageCover64
                                #	#print json.dumps(returnDi)
				#	returnJ=returnDi
					returnJ[KEY_ESIT]=ESIT_OK
                                        returnJ[KEY_RESULT]=SelectS("SELECT picture64 from userimages WHERE user_uid='%s' AND phototype=%d order by userimages.date desc;"%(hvalue(form,'useruid'),PHOTOTYPE_COVER))[0]['picture64']
				except Exception ,e:
					returnJ[KEY_ESIT]=ESIT_ERROR
                                        returnJ[KEY_RESULT]="%s"%e
                        elif cmd==CMD_GETUSERCOVERTHUMB:
                                useruid=tokenfb="%s" % form.getvalue('useruid')
                                returnDi={}
                                image64=UserImageCover(useruid,True)
                                if image64 != '':
                                        returnDi[KEY_ESIT]=ESIT_OK
                                else:
                                        returnDi[KEY_ESIT]=ESIT_ERROR
                                returnDi[KEY_RESULT]=image64
                                #print json.dumps(returnDi)
                                returnJ=returnDi
			elif cmd==CMD_GETUSERINFO:
				returnJ= json.loads(self.UserInfoGet(form))
				#print self.UserInfoGet(form)
			elif cmd==CMD_SIGNUP:
				returnJ= json.loads(self.Signup(form))
				#print self.Signup(form)
			elif cmd==CMD_LOGIN:
				returnJ= self.Signin(form)
				#print self.Signin(form)
			elif cmd==CMD_LOGINTWITTER:
				print self.TwitterLogin(form)
				return
			elif cmd==CMD_UPDATEUSER:
				returnJ= self.UpdateUser(form)
			elif cmd==CMD_CHANGEPASSWORD:
				returnJ= self.PasswordChange(form)
			elif cmd==CMD_GETLEAGUES:
				returnJ=ReturnLeagues()
				#print json.dumps(ReturnLeagues())
			elif cmd==CMD_GETTEAMS:
				returnJ=ReturnTeams(form.getvalue('espnid'))
				#print json.dumps(ReturnTeams(form.getvalue('espnid')))
			elif cmd==CMD_SELECTTEAM:
				returnJ=LikeTeam(form.getvalue('userid'),form.getvalue('teamid'))
				#print json.dumps(LikeTeam(form.getvalue('userid'),form.getvalue('teamid')))
			elif cmd=='ultimaterec': #this function calls change password and select team at the same time
				returnJ= self.PasswordChange(form)
				if returnJ[KEY_ESIT]==ESIT_OK:
					returnJ=LikeTeam(form.getvalue('userid'),form.getvalue('teamid'))
			elif cmd==CMD_ADDPICTURE:
				returnJ=self.AddPicture(form)
				#print self.AddPicture(form)
			elif cmd==CMD_DOCHECKIN:
				returnJ=DoCheckin(form.getvalue('userid'),form.getvalue('businessid'))
				#print json.dumps(DoCheckin(form.getvalue('userid'),form.getvalue('businessid')))
			elif cmd==CMD_GETCHECKIN:
				returnJ=ReturnCheckins(form.getvalue('businessid'),hvalue(form,'useruidmyself'))
				#print json.dumps(ReturnCheckins(form.getvalue('userid')))
			elif cmd==CMD_SENDCHAT:
				returnJ=InsertChat(form.getvalue('fromuser'),form.getvalue('touser'),form.getvalue('message'),form.getvalue('type'),hvalue(form,'synctime'))
				#print json.dumps(InsertChat(form.getvalue('fromuser'),form.getvalue('touser'),form.getvalue('message'),form.getvalue('type')))
			elif cmd==CMD_GETCHAT:
				returnJ=GetChats(form.getvalue('fromuser'),form.getvalue('useruid'),form.getvalue('chatid'))
				#print json.dumps(GetChats(form.getvalue('fromuser'),form.getvalue('useruid'),form.getvalue('chatid')))
			elif cmd==CMD_GETALLCHATS:
				returnJ=GetAllChats(form.getvalue('useruid'))
			elif cmd=='getbusiness':
                                returnJ=GetLocations(form.getvalue('latitude'),form.getvalue('longitude'))
			elif cmd=='follow':
				returnJ=DoFollow(hvalue(form,'useruid'),hvalue(form,'followuid'))
			elif cmd=='unfollow':
                                returnJ=UnFollow(hvalue(form,'useruid'),hvalue(form,'followuid'))
			elif cmd=='myfollowers':
				returnJ=GetFollowers(hvalue(form,'useruid'))
			elif cmd=='whoifollow':
				returnJ=GetFollowing(hvalue(form,'useruid'))	
			elif cmd=='getusertochat':
				returnJ=GetUserToChat(hvalue(form,'useruid'))
			elif cmd=='returnuserfromid':
				dictiD=ReturnUserFromId(hvalue(form,'useruid'))
				try:
					dictiD['iamfollow']=IAmFollow(hvalue(form,'useruidmyself'),hvalue(form,'useruid'))
				except Exception, ee:
					ErrorLog("returnuserfromid %s"%ee)
					dictiD['iamfollow']=-1
				returnJ[KEY_RESULT]=dictiD
				returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='getpeoplemap':
				mp=form.getvalue('maxpeople')
				returnJ=GetPeopleMap(hvalue(form,'useruid'),hvalue(form,'latitude'),hvalue(form,'longitude'),mp)
			elif cmd=='getanyimage':
				returnJ[KEY_RESULT]=GetAnyPicture(hvalue(form,'picid'),hvalue(form,'thumb'))
				returnJ[KEY_ESIT]=self.EsitInsert(returnJ)
			elif cmd=='getalbum':
				returnJ=GetAlbum(hvalue(form,'useruid'),hvalue(form,'phototype'))
			elif cmd=='postwall':
				returnJ=PostOnWall(hvalue(form,'useruid'),hvalue(form,'message'),hvalue(form,'businessId'),hvalue(form,'image64'),hvalue(form,'checkinId'))
			elif cmd=='getwall':
				returnJ=ReturnWall(hvalue(form,'useruid'),hvalue(form,'lastid'))
			elif cmd=='getwallupdate':
                                returnJ=ReturnWallUpdate(hvalue(form,'useruid'),hvalue(form,'lastid'))
			elif cmd=='getpersonalwall':
                                returnJ=ReturnWallPersonal(hvalue(form,'useruid'),hvalue(form,'lastid'))
			elif cmd=='gethash':
				returnJ=GetHash(hvalue(form,'hashkey'),hvalue(form,'lastid'))
			elif cmd=='deletewall':
				returnJ=DeletePost(hvalue(form,'wallid'))
			elif cmd=='deletepicture':
				returnJ=DeletePicture(hvalue(form,'imageid'))
			elif cmd=='getpostfromid':
				returnJ=GetPostFromId(hvalue(form,'postid'))
			elif cmd=='deletechat':
				returnJ=DeleteChat(hvalue(form,'useruid'),hvalue(form,'touseruid'))
			elif cmd=='commentpost':
				returnJ=InsertCommentPost(hvalue(form,'postid'),hvalue(form,'message'),hvalue(form,'useruid'))
			elif cmd=='getcommentspost':
				returnJ=GetCommentPost(hvalue(form,'postid'))
			elif cmd=='viewnotification':
				returnJ=ViewNotification(hvalue(form,'notificationid'))
			elif cmd=='getnotifications':
				returnJ=GetNotifications(hvalue(form,'useruid'))
			elif cmd=='sendtaunt':
				returnJ=SendTaunt(hvalue(form,'useruid'),hvalue(form,'touseruid'))
			elif cmd=='postwallfacebook':
				returnJ=facebook_anto.PostWall(hvalue(form,'fbtoken'),hvalue(form,'useruid'),hvalue(form,'message'))
			elif cmd=='shareappfacebook':
				returnJ[KEY_RESULT]= 'provvisoria'
                                returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='shareappfacebookallfriends':	
				returnJ[KEY_RESULT]= 'provvisoria'
                                returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='getfacebookfriends':
				returnJ[KEY_RESULT]=facebook_anto.GetFriends(hvalue(form,'fbtoken'),hvalue(form,'useruid'))
				returnJ[KEY_ESIT]=self.EsitInsert(returnJ)
			elif cmd=='deletepushtoken':
				returnJ[KEY_RESULT]=QueryS("UPDATE device SET devicetoken=NULL WHERE deviceid='%s';"%(hvalue(form,'deviceiddipadrepio')))
				returnJ[KEY_ESIT]=self.EsitInsert(returnJ)
			elif cmd=='setasprofilepicture':
				returnJ=SetPicAsProfile(hvalue(form,'pictureid'))
				#[KEY_RESULT]=QueryS("UPDATE userimages SET phototype=2,userimages.date=now() WHERE id="+hvalue(form,'pictureid'))
                                #returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='setascoverpicture':
                                returnJ=SetPicAsCover(hvalue(form,'pictureid'))
				#returnJ[KEY_RESULT]=QueryS("UPDATE userimages SET phototype=4,userimages.date=now() WHERE id="+hvalue(form,'pictureid'))
                                #returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='removeuserteam':
				returnJ[KEY_RESULT]= QueryS("DELETE from user_team WHERE user_uid='%s' AND team_id='%s';"%(hvalue(form,'useruid'),hvalue(form,'teamid')))
                                returnJ[KEY_ESIT]=self.EsitInsert(returnJ)
			elif cmd=='errorlog':
				returnJ[KEY_RESULT]= ErrorLog(hvalue(form,'message'))
                                returnJ[KEY_ESIT]=self.EsitInsert(returnJ)
			elif cmd=='repostwall':
				returnJ=RepostWall(hvalue(form,'useruid'),hvalue(form,'postid'))
			elif cmd=='whoreposted':
				returnJ[KEY_RESULT]=WhoReposted(hvalue(form,'postid'))
				returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='searchuser':
				returnJ=SearchUser(hvalue(form,'searcharray'),hvalue(form,'useruid'))
			elif cmd=='isuserregisteredforpush':
				tok=getValueS('device','devicetoken','user_uid',hvalue(form,'useruid'))
				if tok==None or tok=='' :returnJ[KEY_RESULT]= False
				else: returnJ[KEY_RESULT]= True
				returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='getlivescore':
				returnJ=livescore.GetLiveFeed(hvalue(form,'league'))
			elif cmd=='getlivescore2':
				returnJ[KEY_RESULT]=livescore.GetSoccer()# livescore.today(hvalue(form,'league'))
                                returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='getteamfromid':
				returnJ[KEY_RESULT]=SelectS("SELECT team.*,league.name as league_name,league.shortName as league_shortname from team,league where team.id='%s' AND team.league_espn_id=league.espn_id"%hvalue(form,'tiodio'))
				returnJ[KEY_ESIT]=ESIT_OK
			elif cmd=='likewall':
				returnJ=like.LikeWall(hvalue(form,'useruid'),hvalue(form,'wallid'))
			elif cmd=='unlikewall':
                                returnJ=like.UnlikeWall(hvalue(form,'useruid'),hvalue(form,'wallid'))
			elif cmd=='block':
				returnJ=block.Block(hvalue(form,'useruid'),hvalue(form,'blockuid'))
			elif cmd=='unblock':
                                returnJ=block.Unblock(hvalue(form,'useruid'),hvalue(form,'blockuid'))
			elif cmd=='blacklist':
                                returnJ=block.BlackList(hvalue(form,'useruid'))
			elif cmd=='updateuserteams':
				returnJ['actions']=InsertDeleteTeams(hvalue(form,'userid'),hvalue(form,'addedteams'),hvalue(form,'deletedteams'))
				returnJ[KEY_RESULT]=ReturnUserTeams(hvalue(form,'userid'))
				returnJ[KEY_ESIT]=ESIT_OK
			else:
                       	 	returnJ[KEY_RESULT]= 'error command unknown'
				returnJ[KEY_ESIT]=ESIT_ERROR
		#add extra data to the result:
		returnJ=self.AddToResult(returnJ)
		#update the last time seen user online
		userid_key=hvalue(form,'useridkey')
		#if userid_key!=None : 
		self.UpdateOnline(userid_key,form.getvalue('latitudekey'),form.getvalue('longitudekey'))
		#ErrorLog("%s"%form.getvalue('latitudekey')+" "+"%s"%form.getvalue('longitudekey')+" "+"%s"%userid_key)		
		returnJ['unread_chats']=GetUnread(userid_key)
		returnJ['unread_notifications']=GetNotificationCount(userid_key)
		returnJ[KEY_CMD]=cmd
		print json.dumps(returnJ)
	

	#--------------------------------------------------------------------
        #-----ADD extra info to the result
        def AddToResult(self,returnJ):
		try:
			if returnJ[KEY_ESIT]!=ESIT_OK : return returnJ
			queryAr=returnJ[KEY_RESULT] 
			if type(queryAr) is dict:
                		#if 'uid' in queryAr:
				#	queryAr['userprofilepic_id']=GetProfilePicId(queryAr['uid'])#SelectS("SELECT id from userimages WHERE user_uid=%s ORDER BY userimages.date DESC"%queryAr['uid'])[0]['id']
        			#if 'user_uid' in queryAr:
                                #        queryAr['userprofilepic_id']=getValueS('userimages','id','user_uid',"%s"%queryAr['user_uid'])
				returnJ[KEY_RESULT]=self._extractPhotoId(queryAr)#queryAr
			elif is_array(queryAr):
				if len(queryAr)==0 : return returnJ
				resultA=[]
				for row in queryAr:
					#if 'uid' in row:
                                	#	row['userprofilepic_id']=getValueS('userimages','id','user_uid',"%s"%row['uid'])
					#if 'user_uid' in row:
					#	row['userprofilepic_id']=getValueS('userimages','id','user_uid',"%s"%row['user_uid'])
					resultA.append(self._extractPhotoId(row))#(row)
				returnJ[KEY_RESULT]=resultA
		except Exception,e:
			#ErrorLog("addtoresult, %s"%e)
			returnJ['anyerror']="%s"%e
		return returnJ

	def _extractPhotoId(self,queryAr):
		key=''
		if 'uid' in queryAr:key='uid'
		elif 'user_uid' in queryAr:key='user_uid'
                queryAr['userprofilepic_id']=GetProfilePicId(queryAr[key])
		return queryAr
	
 	#--------------------------------------------------------------------
        #-----SECURITY FUNCTION AUTHENTICATION
	def Authenticate(self,form):
        	if form.getvalue('parolamagica')=='abracadabra':return True

		secdeviceid=form.getvalue('patatadeviceid')
        	sectoken=form.getvalue('patatatoken')
        	secsync=form.getvalue('patatasync')

        	if(sectoken==None):return False
		if(secdeviceid==None):return False
		if(secsync==None):return False
		if(len(secdeviceid)<11): return False		

        	mdS=secdeviceid+securityString1+secsync+securityString2
        	m = hashlib.md5()
        	m.update(mdS)
        	criptedS= m.hexdigest()
        	if criptedS==sectoken: return True
        	return False

	#--------------------------------------------------------------------
        #-----INSERT RETURN CHECK
        def EsitInsert(self,dicty):
		if (dicty[KEY_RESULT]==-1 or dicty[KEY_RESULT]==None):return ESIT_ERROR
		return ESIT_OK

 	#--------------------------------------------------------------------
        #-----
	def UpdateOnline(self,useruid,latitude,longitude):
		if useruid==None : return
        	cursor=self.DB().cursor(MySQLdb.cursors.DictCursor)
        	sql="UPDATE user SET lastonline=now() WHERE uid=%s;"%useruid
        	try:
                	cursor.execute(sql)
                	db.commit()
        	except:
                	db.rollback()
        	cursor.close()
		
		if latitude==None : return
		if longitude==None : return
		cursor=self.DB().cursor(MySQLdb.cursors.DictCursor)
                sql="UPDATE user SET latitude=%s,longitude=%s WHERE uid=%s;"%(latitude,longitude,useruid)
                try:
                        cursor.execute(sql)
                        #userid=db.insert_id()
                        db.commit()
                except:
                        db.rollback()
                cursor.close()

 	#--------------------------------------------------------------------
        #-----	
        def AddPicture(self,form):
                responseJ={}
		responseJ[KEY_ESIT]=ESIT_OK
                responseJ[KEY_RESULT]=UploadImage(form.getvalue('useruid'),form.getvalue('image'),form.getvalue('type'))
                if responseJ[KEY_RESULT]==-1:
			responseJ[KEY_ESIT]=ESIT_ERROR
		else:
			responseJ[KEY_ESIT]=ESIT_OK
		return responseJ
		#df=json.dumps(responseJ)
                #return df

	#--------------------------------------------------------------------
        #----- 
	def PasswordChange(self,form):
		responseJ={}
		responseJ[KEY_ESIT]=UpdatePassword(form.getvalue('password'),form.getvalue('oldpassword'),form.getvalue('userid'))
		#df=json.dumps(responseJ)
                return responseJ

	#--------------------------------------------------------------------
        #----- 
	def UpdateUser(self,form):
		responseJ={}
		responseJ[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
		dicti=UserUpdate(form.getvalue('userid'),form.getvalue('username'),form.getvalue('password'),form.getvalue('firstname'),form.getvalue('lastname'),form.getvalue('gender'),form.getvalue('nationality'),form.getvalue('dob'),form.getvalue('latitude'),form.getvalue('longitude'),form.getvalue('currentcity'),form.getvalue('hometown'),form.getvalue('fbid'),form.getvalue('twitterid'),form.getvalue('occupation'),form.getvalue('aboutme'),form.getvalue('relationship'),form.getvalue('state'),form.getvalue('active'),form.getvalue('showlocation'))	
		
		responseJ[KEY_ESIT]=dicti[KEY_ESIT]
		responseJ[KEY_RESULT]=dicti
		#df=json.dumps(responseJ)
		#return df
		return responseJ

	#--------------------------------------------------------------------
        #----- 	
	def TwitterLogin(self,form):
		responseJ={}
                responseJ[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
                username="%s" % form.getvalue('username')
                email=form.getvalue('email')
                twitid=form.getvalue('twitterid')
		tokenT=form.getvalue('twittertoken')
                dicti=RegisterUser(username,email,twitid,tokenT)
                try:    
                        esitT=dicti['esit_register']
                        responseJ['twitter']=dicti
                        
                        if esitT==ESIT_OK:
				updateUserD=UserUpdate(dicti['uid'],form.getvalue('username'),form.getvalue('password'),form.getvalue('firstname'),form.getvalue('lastname'),form.getvalue('gender'),form.getvalue('nationality'),form.getvalue('dob'),form.getvalue('latitude'),form.getvalue('longitude'),form.getvalue('currentcity'),form.getvalue('hometown'),form.getvalue('fbid'),form.getvalue('twitterid'),form.getvalue('occupation'),form.getvalue('aboutme'),form.getvalue('relationship'),form.getvalue('state'),form.getvalue('active'),form.getvalue('showlocation'))

				esitU=updateUserD[KEY_ESIT]
				if esitU==ESIT_ERROR:
					responseJ[KEY_ESIT]=ESIT_EXSIST
				else:
					responseJ[KEY_ESIT]=ESIT_OK
				responseJ[KEY_RESULT]=updateUserD
			else:
				responseJ[KEY_ESIT]=esitT
				responseJ[KEY_RESULT]=dicti
				df=json.dumps(responseJ)
				return df
                except Exception,r:
			ErrorLog('exception: %s'%r)
                        responseJ[KEY_ESIT]=ESIT_ERROR
                        responseJ[KEY_RESULT]='exception '%r
                        return json.dumps(responseJ)


	#--------------------------------------------------------------------
        #----- 
        def Signup(self,form):
                responseJ={}
                responseJ[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
                username= form.getvalue('username')
		if username==None:username=id_generator()
		email=form.getvalue('email')
		password=form.getvalue('password')
		dicti=RegisterUser(username,email,password)
                try:
			responseJ[KEY_ESIT]=dicti['esit_register']
                        responseJ[KEY_RESULT]=dicti
                        df=json.dumps(responseJ)
			#follow the admin
			self.FollowAdmin(ReturnUserUidFromEmail(email))
                        return df
                except Exception,e:
                        responseJ[KEY_ESIT]=ESIT_ERROR
                        responseJ[KEY_RESULT]='exception: %s'%e
			ErrorLog('exception: %s'%e)
                        return json.dumps(responseJ)


	#--------------------------------------------------------------------
        #-----
	def FollowAdmin(self,useruid):
		DoFollow("%s"%useruid,'5771')

	#--------------------------------------------------------------------
        #----- 
        def Signin(self,form):
                responseJ={}
                #responseJ[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
                email=form.getvalue('email').lower()
                password=form.getvalue('password')
                dicti=LoginUser(email,password)
		responseJ={}
                try:
			isvalid = (dicti and True) or False
			esitN=ESIT_EXIST
			if isvalid:esitN=dicti[KEY_ESIT]#ESIT_OK
			responseJ[KEY_ESIT]=esitN
                        responseJ[KEY_RESULT]=dicti
                        #df=json.dumps(responseJ)
                except Exception,e:
			ErrorLog("Api.py Signin,exception:%s"%e)
                        responseJ[KEY_ESIT]=ESIT_ERROR
                        responseJ[KEY_RESULT]='exception'
                return responseJ


	#--------------------------------------------------------------------
        #----- 
        def UserInfoGet(self,form):
                responseJ={}
                responseJ[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
                userid="%s" % form.getvalue('useruid')
                dicti = ReturnUserFromId(userid)
                try:
                        responseJ[KEY_ESIT]=ESIT_OK
			responseJ[KEY_RESULT]=dicti
                        df=json.dumps(responseJ)
                        return df
                except:
                        responseJ[KEY_ESIT]=ESIT_ERROR
                        responseJ[KEY_RESULT]='exception'
                        return json.dumps(responseJ)

	#--------------------------------------------------------------------
        #----- 
	def LoginFB(self,form):
		responseJ={}
		responseJ[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
		tokenfb="%s" % form.getvalue('tokenfb')
                dicti = SignUpFbToken(tokenfb)
		try:
			if dicti['new_user']==True:
				responseJ[KEY_ESIT]=ESIT_OK
				try:
                                	#follow the admin
                                	self.FollowAdmin(dicti['uid'])
                        	except Exception,ll:
                                	ErrorLog('LoginFB follow admin , exception :%s'%ll)
			if dicti['new_user']==False:
                                responseJ[KEY_ESIT]=ESIT_EXIST
			responseJ[KEY_RESULT]=dicti
			df=json.dumps(responseJ)
			return df
		except Exception,e:
			ErrorLog('LoginFB , exception :%s'%e)
			responseJ[KEY_ESIT]=ESIT_ERROR
			responseJ[KEY_RESULT]='exception :%s'%e
			return json.dumps(responseJ)

	#--------------------------------------------------------------------
        #-----  
	def RegisterToken(self,form):
                responseJ={}
                responseJ[KEY_CMD]="%s" % form.getvalue(KEY_CMD)
                tokenS=hvalue(form,'token')#form.getvalue("token")
                typeS=form.getvalue("type")
                deviceId=hvalue(form,'deviceid')#UrlDecode(form.getvalue("deviceid"))
                userUid=form.getvalue("useruid")
                development=""+form.getvalue("development")
                version=hvalue(form,'version')#form.getvalue("version")
                sql=''
		mapex={}
		mapex['deviceid']=deviceId
		if exists('device',mapex)==True:
			mapex['devicetoken']=tokenS
			if exists('device',mapex)==False:
				sql="UPDATE device SET development='%s',devicetoken='%s' WHERE deviceid='%s';"%(development,tokenS,deviceId)	
		else:
			sql="INSERT INTO device (development,devicetype,deviceid,devicetoken,user_uid,version) VALUES ('%s','%s','%s','%s','%s','%s');"%(development,typeS,deviceId,tokenS,userUid,version)

		if sql=='':
			responseJ[KEY_ESIT]=ESIT_EXIST
			return responseJ
		responseJ[KEY_RESULT]=sql	
		cursor=self.DB().cursor(MySQLdb.cursors.DictCursor)
                try:
                        cursor.execute(sql)
                        db.commit()
                        responseJ[KEY_ESIT]=ESIT_OK
                except:
                        db.rollback()
                        responseJ[KEY_ESIT]=ESIT_ERROR
                finally:
                        cursor.close()

                return responseJ


        #--------------------------------------------------------------------
        #-----
        def TestConnection(self,form):
                cursor=self.DB().cursor(MySQLdb.cursors.DictCursor)
                sql="SELECT * FROM user;"
                try:
                        cursor.execute(sql)
                        result = RetJson(cursor)
                        dd={}
                        dd[KEY_ESIT]=ESIT_OK
                        dd[KEY_CMD]=cmd="%s" % form.getvalue(KEY_CMD)
                        dd[KEY_RESULT]=result
                        return json.dumps(dd)
                except:
                        return "exception"
                finally:
                        cursor.close()

	#--------------------------------------------------------------------
        #-----
        def SaveFbHash(self,form):
		cursor=self.DB().cursor(MySQLdb.cursors.DictCursor)
                hashS=form.getvalue("hash")
                try:
                        f=open('hash_fb.txt','a')
			f.write("%s\n"% hashS)
			f.close()
			return 'ok'
			#dd={}
                        #dd[KEY_ESIT]=0
                        #dd[KEY_CMD]=cmd="%s" % form.getvalue(KEY_CMD)
                        #dd[KEY_RESULT]=hashS
                        #return json.dumps(dd)
                except:
                        return "exception"
		finally:
                        cursor.close()

#-----END of the Api class              
#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def main():
        print "Content-type:application/json\r\n\r\n"
        try:
                api=Api()
                #with api.DB():
                api.HandleCommand()
                api.DBclose()
                del api
        except Exception,exc:
                de={}
                de[KEY_ESIT]=ESIT_ERROR
                de[KEY_RESULT]="error main() exception , error:%s"%exc
		ErrorLog(de[KEY_RESULT])
                print json.dumps(de)
		if db.open:
			db.close()

        if db.open:
                print 'databse not closed!'


#----------------------------------------------------------------------------
#-----START the script

if __name__ == '__main__':
    main()

#----------------------------------------------------------------------------

                             
