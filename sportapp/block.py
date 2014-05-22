#!/usr/bin/python
# -*- coding: utf-8 -*-
from defs import *
from database import *
from utility import *
from notification import InsertNotification

def Block(useruid,blockuid):
        mapI={}
        dicty={}
        dicty[KEY_ESIT]=ESIT_OK
        mapI['user_uid']=useruid
        mapI['blocked_user_uid']=blockuid
        dicty[KEY_RESULT]=Insert('block',mapI)
        if (dicty[KEY_RESULT]==-1 or dicty[KEY_RESULT]==None):
                dicty[KEY_ESIT] = ESIT_ERROR
        return dicty

def Unblock(useruid, blockuid):
        dicty={}
        dicty[KEY_ESIT]=ESIT_OK
        dicty[KEY_RESULT] = QueryS("DELETE from block WHERE user_uid='%s' AND blocked_user_uid='%s';"%(useruid,blockuid))
        if (dicty[KEY_RESULT]==-1 or dicty[KEY_RESULT]==None):dicty[KEY_ESIT] = ESIT_ERROR
        return dicty

def BlackList(useruid):
	dicty={}
        dicty[KEY_ESIT]=ESIT_OK
        dicty[KEY_RESULT] = SelectS("SELECT user.* from user,block WHERE user_uid='%s' and blocked_user_uid=user.uid"%useruid)
	return dicty

