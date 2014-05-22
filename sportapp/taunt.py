#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
from defs import *
from database import *
from utility import *
from notification import InsertNotification
import time

def SendTaunt(fromuser,touser):
	mapI={}
	testTime=SelectS("SELECT max(date) as dateM from taunt WHERE id_sender='%s' and id_receiver='%s';"%(fromuser,touser))
	timeL=testTime[0]['dateM']
	if timeL==None: timeL=111111
	nowT=time.time()
	if (nowT-timeL)<1500:
		mapI[KEY_ESIT]=ESIT_EXIST
		mapI[KEY_RESULT]='too many taunts'
		return mapI
	mapI['id_sender']=fromuser
	mapI['id_receiver']=touser
	mapI[KEY_RESULT]=Insert('taunt',mapI)
        mapI[KEY_ESIT]=ESIT_OK
        if mapI[KEY_RESULT]==-1 : 
		mapI[KEY_ESIT]=ESIT_ERROR
	else:
		InsertNotification("Someone sent you a taunt",NOTIF_TYPETAUNT,fromuser,fromuser,touser)
	return mapI

