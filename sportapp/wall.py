#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
from defs import *
from database import *
from utility import *
from images import *
from user import UploadImage
from location import GetBusinessFromDatabase
from notification import InsertNotification
import like
import pictures

#-------------------------------------------------------------------------
#--------------
def repostId(postid):
	#first of all check if this is already a repost
        #if it's a repost take the original and repost from that one
	if existsS('wall_repost','repost_id',postid):
                postid="%d"%SelectS("SELECT wall_id FROM wall_repost WHERE repost_id='%s';"%postid)[0]['wall_id']
	return postid

#-------------------------------------------------------------------------
#--------------
def TotalReposts(postid):
	return SelectS("SELECT count(*) as total from wall_repost where wall_id='%s'"%repostId(postid))[0]['total']

#-------------------------------------------------------------------------
#--------------
def WhoReposted(postid):
	return SelectS("SELECT wall_repost.*,user.uid as originalpost_useruid,user.username as repost_username, user.firstname as repost_name , user.lastname as repost_last from wall_repost,user,wall where wall_id='%s' AND user.uid=repost_user_uid AND wall.id=wall_id"%repostId(postid))

#-------------------------------------------------------------------------
#--------------
def RepostWall(useruid,postid):
	postid=repostId(postid)

	wallpA=SelectS("SELECT * FROM wall where id='"+postid+"'")
	message="repost from : @[\"%s\",\"%s\"]<br> %s"%(getValueS('user','username','uid',"%s"%wallpA[0]['user_uid']),"%s"%wallpA[0]['user_uid'],wallpA[0]['message'])
	image64=''
	if wallpA[0]['userimages_id']!=None:
		image64=getValueS('userimages','picture64','id',"%s"%wallpA[0]['userimages_id'])
	else:
		image64=None
	returnRep= PostOnWall(useruid,message,wallpA[0]['business_idapi'],image64,"%s"%wallpA[0]['checkinlog_id'])
	
	try:
                mapi={}
                mapi['wall_id']=postid
                mapi['repost_id']="%s"%returnRep[KEY_RESULT]
                mapi['repost_user_uid']=useruid
		Insert('wall_repost',mapi)
		try:
			InsertNotification("Someone reposted your post",NOTIF_TYPEREPOST,postid,useruid,"%s"%row['user_uid'])
		except:
			ErrorLog("Wall file, repostWall, insert notification")
        except:
                ErrorLog("Wall file, repostWall, insert into the wallrepost table")

	return returnRep

#-------------------------------------------------------------------------
#--------------
def Notify(postid,useruid):
	#results=SelectS("SELECT comments.*,wall.user_uid as walluseruid from comments WHERE wall_id=%s AND walluseruid!=%s GROUP BY user_uid"%(postid,useruid))
	results=SelectS("SELECT comments.*,wall.user_uid as walluseruid from comments,wall WHERE wall_id=%s AND wall.user_uid!=%s AND wall.id=comments.wall_id GROUP BY user_uid"%(postid,useruid))
	if(len(results)>0):
		InsertNotification("Someone commented your post",NOTIF_TYPECOMMENT,postid,useruid,"%s"%results[0]['walluseruid'])
		for row in results:
			if("%s"%row['user_uid']!=useruid):
				InsertNotification("Someone commented after you",NOTIF_TYPECOMMENT,postid,useruid,"%s"%row['user_uid'])

#-------------------------------------------------------------------------
#--------------get the post from the given id
def GetPostFromId(postid):
	dicty={}
	try:
		useruid="%s"%getValueS('wall','user_uid','id',postid)
		sql="select * from((SELECT wall. * , imm.user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll, (SELECT MAX( id ) AS user_picture_id, user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AS imm WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.id = %s AND imm.imm_user_uid = user_uid GROUP BY wall.id ORDER BY wall.date desc) UNION (SELECT wall. * ,NULL as user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.id =%s AND user_uid NOT IN (SELECT  user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) GROUP BY wall.id ORDER BY wall.date desc)) as wallres ORDER BY wallres.date desc limit 0,30"%(useruid,postid,useruid,postid)
		results=SelectS(sql)
		if len(results)>0 : 
			dicty[KEY_RESULT]=ConstructWallResult(results)[0]#results[0]
			mapE={}
			mapE['user_uid']=useruid
			mapE['wall_id']=postid
			dicty['ilikeit']=exists('like_wall_user',mapE)
			dicty['totallike']=like.TotalLike(postid)
			dicty['whoreposted']=WhoReposted(postid)
			dicty['totalreposts']=len(dicty['whoreposted'])
			dicty[KEY_ESIT]=ESIT_OK
		else:
			dicty[KEY_ESIT]=ESIT_EXIST
			dicty[KEY_RESULT]='post id does not exist'
	except Exception,e:
		ErrorLog("getpostfromid")
		dicty[KEY_RESULT]="%s"%e
		dicty[KEY_ESIT]=ESIT_ERROR
	return dicty
#-------------------------------------------------------------------------
#--------------
def InsertCommentPost(postid,message,useruid):
	delH={}
	delH['wall_id']=postid
	delH['text']=message
	delH['user_uid']=useruid
	delH[KEY_RESULT]=Insert('comments',delH)
	delH['comments']=GetCommentPost(postid)
        delH[KEY_ESIT]=ESIT_OK
	Notify(postid,useruid)
        return delH

#-------------------------------------------------------------------------
#--------------
def GetCommentPost(postid):
        delH={}
        delH['wall_id']=postid
        delH[KEY_RESULT]=SelectS("SELECT * FROM ((SELECT comments.*,imm.user_picture_id,user.username,user.firstname,user.lastname FROM comments,user,(SELECT MAX( id ) AS user_picture_id, user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AS imm WHERE wall_id=%s AND user.uid=user_uid AND imm.imm_user_uid = user.uid GROUP BY comments.id ORDER BY comments.date DESC) UNION (SELECT comments.*,NULL as user_picture_id,user.username,user.firstname,user.lastname FROM comments,user WHERE wall_id=%s AND user.uid=user_uid AND user.uid NOT IN (SELECT user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2)))as crazy GROUP BY id ORDER BY crazy.date DESC"%(postid,postid))
        delH[KEY_ESIT]=ESIT_OK
        return delH

#-------------------------------------------------------------------------
#--------------
def CountCommentPost(postid):
        delH=SelectS("SELECT count(*) as total FROM comments WHERE wall_id=%s"%postid)
        return delH[0]['total']


#-------------------------------------------------------------------------
#--------------
def DeletePost(postid):
	delH={}
	delH['id']=postid
	delH[KEY_RESULT]=Delete('wall',delH)
        delH[KEY_ESIT]=ESIT_OK
	return delH

#-------------------------------------------------------------------------
#--------------
def GetHash(keyhash,lastid=-1):
        if lastid==None : lastid=SelectS("SELECT MAX(id) as maxid from wall")[0]['maxid']
	if int(lastid)==-1 : lastid=SelectS("SELECT MAX(id) as maxid from wall")[0]['maxid']
	
	sql="SELECT * from ((SELECT wall. * , imm.user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, hashtag, (SELECT MAX( id ) AS user_picture_id, user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AS imm WHERE user.uid = user_uid AND LOWER(hash) = LOWER('%s') AND wall.id = hashtag.wall_id AND wall.id<=%s AND imm.imm_user_uid = user.uid GROUP BY wall.id ORDER BY wall.date DESC) UNION (SELECT wall. * , NULL as user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, hashtag WHERE user.uid = user_uid AND LOWER(hash) =  LOWER('%s') AND wall.id = hashtag.wall_id AND user.uid NOT IN (SELECT user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AND wall.id<=%s GROUP BY wall.id ORDER BY wall.date DESC))as wallres ORDER BY wallres.date desc limit 0,30"%(keyhash,lastid,keyhash,lastid)
	hashA=SelectS(sql)
	dicty={}
	dicty[KEY_RESULT]=ConstructWallResult(hashA)#resultA
        dicty[KEY_ESIT]=ESIT_OK
	return dicty



#-------------------------------------------------------------------------
#--------------
def ReturnWallAll(lastid=-1):
        db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)

	sql="select * from((SELECT wall. * , imm.user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT MAX( id ) AS user_picture_id, user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AS imm WHERE user.uid = user_uid  AND wall.id > %s AND imm.imm_user_uid = user_uid GROUP BY wall.id ORDER BY wall.date desc) UNION (SELECT wall. * ,NULL as user_picture_id, user.username, user.firstname, user.lastname FROM wall, user WHERE user.uid = user_uid AND wall.id >%s AND user_uid NOT IN (SELECT  user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) GROUP BY wall.id ORDER BY wall.date desc)) as wallres ORDER BY wallres.date desc limit 0,30"%(lastid,lastid)

        dicty={}
        results=[]
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
                results=DateToLong(results)
                dicty[KEY_RESULT]=ConstructWallResult(results)#resultA
                dicty[KEY_ESIT]=ESIT_OK
        except:
                dicty[KEY_ESIT]=ESIT_ERROR
        cursor.close()
        db.close()
        return dicty


#-------------------------------------------------------------------------
#--------------
def ReturnWallUpdate(useruid,lastid=-1):
	if lastid==None : lastid=-1
        if lastid==-1 or lastid=='0':
		dates="0"
	else:
		dates= getValueS('wall','date','id',"%s"%lastid)
	if dates=='':
		return ReturnWall(useruid)
	
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)

	sql="select * from((SELECT wall. * , imm.user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll, (SELECT MAX( id ) AS user_picture_id, user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AS imm WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.date > '%s' AND imm.imm_user_uid = user_uid GROUP BY wall.id ORDER BY wall.date desc) UNION (SELECT wall. * ,NULL as user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.date >'%s' AND user_uid NOT IN (SELECT  user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) GROUP BY wall.id ORDER BY wall.date desc)) as wallres ORDER BY wallres.date desc limit 0,30"%(useruid,dates,useruid,dates)

	dicty={}
        results=[]
        try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
		results=DateToLong(results)
                dicty[KEY_RESULT]=ConstructWallResult(results,useruid)#resultA
		dicty[KEY_ESIT]=ESIT_OK
        except Exception,e:
		ErrorLog("ReturnWallUpdate Exception: %s"%e)
                dicty[KEY_ESIT]=ESIT_ERROR
        cursor.close()
        db.close()
	
	#if the user has no posts we return the all wall
	#try:
	#	if (len(ReturnWallPersonal(useruid)[KEY_RESULT])==0): return ReturnWallAll(lastid)
        #except Exception ,d:
	#	ErrorLog("%s"%d)
	return dicty


#-------------------------------------------------------------------------
#--------------
def ReturnWallPersonal(useruid,lastid=-1):
        if lastid==None : lastid=-1
	sql="select * from((SELECT wall. * , imm.user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll, (SELECT MAX( id ) AS user_picture_id, user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AS imm WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.id > %s AND imm.imm_user_uid = user_uid GROUP BY wall.id ORDER BY wall.date desc) UNION (SELECT wall. * ,NULL as user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid = '%s' GROUP BY user.uid) AS foll WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.id >%s AND user_uid NOT IN (SELECT  user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) GROUP BY wall.id ORDER BY wall.date desc)) as wallres WHERE user_uid = '%s' ORDER BY wallres.date desc limit 0,30"%(useruid,lastid,useruid,lastid,useruid)
	dicty={}
        results=[]
        try:
                results=SelectS(sql)
		dicty[KEY_RESULT]=ConstructWallResult(results,useruid)
                dicty[KEY_ESIT]=ESIT_OK
        except:
                dicty[KEY_ESIT]=ESIT_ERROR
        return dicty

#-------------------------------------------------------------------------
#--------------
def ReturnWall(useruid,lastid=-1):
	if lastid==None : lastid=-1
	db=MySQLdb.connect(host=HOST,user=DBUSER,passwd=DBPASS,db=DBNAME, use_unicode=True,charset="utf8")
        cursor=db.cursor(MySQLdb.cursors.DictCursor)
	#sql="(SELECT wall. * , imm.user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll, (SELECT MAX( id ) AS user_picture_id, user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AS imm WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.id > %s AND imm.imm_user_uid = user_uid GROUP BY wall.id ORDER BY DATE DESC) UNION (SELECT wall. * ,NULL as user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.id > %s AND user_uid NOT IN (SELECT  user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) GROUP BY wall.id ORDER BY DATE DESC)"%(useruid,lastid,useruid,lastid)	
	sql="select * from((SELECT wall. * , imm.user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll, (SELECT MAX( id ) AS user_picture_id, user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) AS imm WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.id <%s AND imm.imm_user_uid = user_uid GROUP BY wall.id ORDER BY wall.date desc) UNION (SELECT wall. * ,NULL as user_picture_id, user.username, user.firstname, user.lastname FROM wall, user, (SELECT user.firstname, user.lastname, user.username, user.uid FROM  `follow` , user WHERE (follow_user_uid = user.uid OR user.uid = user_uid) AND user_uid =  '%s' GROUP BY user.uid) AS foll WHERE user.uid = user_uid AND foll.uid = wall.user_uid AND wall.id <%s AND user_uid NOT IN (SELECT  user_uid AS imm_user_uid FROM userimages WHERE  `phototype` =2 GROUP BY imm_user_uid) GROUP BY wall.id ORDER BY wall.date desc)) as wallres ORDER BY wallres.date desc limit 0,30"%(useruid,lastid,useruid,lastid)
	dicty={}
	results=[]
	try:
                queryEsit=cursor.execute(sql)
                results=cursor.fetchall()
        	results=DateToLong(results)
		#resultA=[]
		#for row in results:
		#	#add the business info
		#	if row['business_idapi']!=None:
		#		row['location_present']=True
		#		row['location']=GetBusinessFromDatabase(row['business_idapi'])
		#	else:
		#		row['location_present']=False
		#	resultA.append(row)
		#	#add the checkin info
		#	if row['checkinlog_id']!=0:
		#		row['checkin_present']=True
		#		checkinInfo=SelectS("SELECT * FROM checkinlog WHERE id=%s"%row['checkinlog_id'])
		#		dictx={}
		#		dictx=GetBusinessFromDatabase(checkinInfo[0]['business_id'])
		#		dictx['checkin_date']=checkinInfo[0]['date']
		#		row['checkin']=dictx
		#	else:
		#		row['checkin_present']=False
		dicty[KEY_RESULT]=ConstructWallResult(results,useruid)#resultA
		dicty[KEY_ESIT]=ESIT_OK	
	except:
                dicty[KEY_ESIT]=ESIT_ERROR
        cursor.close()
        db.close()

	#if no results return the all wall
        #if len(dicty[KEY_RESULT])==0: return ReturnWallAll()
	#if the user has no posts we return the all wall
        try:
                if (len(ReturnWallPersonal(useruid)[KEY_RESULT])==0): return ReturnWallAll(lastid)
        except Exception ,d:
                ErrorLog("%s"%d)
	return dicty

#-------------------------------------------------------------------------
#--------------
def ConstructWallResult(results,useruid=0):
	resultA=[]
	try:
                for row in results:
			#add if i like it
			mapE={}
                        mapE['user_uid']=useruid#row['user_uid']
                        mapE['wall_id']=row['id']
                        row['ilikeit']=exists('like_wall_user',mapE)
			row['totallike']=like.TotalLike(row['id'])
                        if 'newsid' in row:
				row['isnews']=False
				if row['newsid']!=0:
					row['isnews']=True
					row['news_link']=getValueS('newslinks','link','wall_id',row['id'])
					if row['news_link']=="":row['isnews']=False
			#count the total reposts
			row['totalreposts']=TotalReposts(row['id'])
			#add the business info
                        if row['business_idapi']!=None:
                                row['location_present']=True
                                row['location']=GetBusinessFromDatabase(row['business_idapi'])
                        else:
                                row['location_present']=False
                        #add the checkin info
                        if row['checkinlog_id']!=0:
                                row['checkin_present']=True
                                checkinInfo=SelectS("SELECT * FROM checkinlog WHERE id=%s"%row['checkinlog_id'])
                                dictx={}
                                dictx=GetBusinessFromDatabase(checkinInfo[0]['business_id'])
                                dictx['checkin_date']=checkinInfo[0]['date']
                                row['checkin']=dictx
                        else:
                                row['checkin_present']=False
			#count the comments
			row['howmanycomments']=CountCommentPost("%s"%row['id'])
                	resultA.append(row)
		return resultA
        except:
                return resultA


#-------------------------------------------------------------------------
#--------------
def PostOnWall(useruid,message,businessId,image64,checkinId,isNews=False,newsId=0,dateNews=None):
	retM={}
	try:
		mapIns={}

		if isNews:
                        if(existsS('wall','newsid',"%s"%newsId)):return None
                        mapIns['newsid']="%s"%newsId
                        if dateNews!=None: mapIns['date']=dateNews

		if image64!=None:mapIns['userimages_id']="%s"%UploadImage(useruid,pictures.ResizeImg64(image64,750),"%s"%PHOTOTYPE_POST)
		mapIns['user_uid']=useruid
		mapIns['message']=message
		if(businessId!=None):mapIns['business_idapi']=businessId
		if(checkinId!=None):mapIns['checkinlog_id']=checkinId
		#retM={}
		retM[KEY_RESULT]=Insert('wall',mapIns)
		if retM[KEY_RESULT]==-1:
			retM[KEY_ESIT]=ESIT_ERROR
		else:
			retM[KEY_ESIT]=ESIT_OK
			retM['hashtags']=ExtractHashTagI(message,"%s"%retM[KEY_RESULT])
		#return retM
	except Exception,e:
		ErrorLog("%s"%e)
		retM[KEY_RESULT]="%s"%e
                retM[KEY_ESIT]=ESIT_ERROR
	return retM

#-------------------------------------------------------------------------
#--------------
def ExtractHashTagI(message,wallid):
	setH=ExtractHashTags(message)
	if len(setH)==0:return 0
	insR=-1
	for hh in setH:
		mapI={}
		mapI['hash']=hh
		mapI['wall_id']=wallid
		insR=Insert('hashtag',mapI)
	if insR!=-1:return len(setH)
	return -1	
