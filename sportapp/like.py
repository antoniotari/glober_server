#!/usr/bin/python
# -*- coding: utf-8 -*-
from defs import *
from database import *
from utility import *
from notification import InsertNotification

def LikeWall(useruid,wallid):
	#ErrorLog(useruid)
	mapI={}
	dicty={}
	dicty[KEY_ESIT]=ESIT_OK
	mapI['user_uid']=useruid
	mapI['wall_id']=wallid
	dicty[KEY_RESULT]=Insert('like_wall_user',mapI)
	if (dicty[KEY_RESULT]==-1 or dicty[KEY_RESULT]==None):
		dicty[KEY_ESIT] = ESIT_ERROR	
	return dicty

def UnlikeWall(useruid, wallid):
	dicty={}
        dicty[KEY_ESIT]=ESIT_OK
	dicty[KEY_RESULT] = QueryS("DELETE from like_wall_user WHERE user_uid='%s' AND wall_id='%s';"%(useruid,wallid))
	if (dicty[KEY_RESULT]==-1 or dicty[KEY_RESULT]==None):dicty[KEY_ESIT] = ESIT_ERROR
        return dicty

def TotalLike(wallid):
	return SelectS("SELECT count(*) as total from like_wall_user WHERE wall_id='%s'"%wallid)[0]['total']
