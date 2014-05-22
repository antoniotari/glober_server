#!/usr/bin/python

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
#-----CONSTANTS
HOST=           'localhost'
DBUSER=         'antonio'
DBPASS=         'glorious.and.free'
DBNAME=         'sportapp'

KEY_ESIT=       'esit'
KEY_RESULT=     'result'
KEY_CMD=        'cmd'

GOOGLE_API_KEY=	'AIzaSyBGg-A5iwi5jEDX_G44ekc0uBgUJ-6j8Rk'
ESPN_API_KEY=	'ufuancvzf7xb58f9zh7khr32'
#db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)

FILE_DEFAULTS_URL=      '/media/hd2/sportapp/sportappdefaults.xml'

BASE_URL=               "http://162.216.4.195"
CHAT_IMAGE_KEY=         "afsjktirntly845kfhtk594jrtjh49lrtj4955555555klrktlrjkkjhhjkhgjh"
UPLOAD_IMAGE_URL=       "http://162.216.4.195/sex/img/profilepic/images/"
BASE_PICTURE_DIR=       "/media/hd2/sportapp/img/profilepic/"
UPLOAD_IMAGE_DIR=       "images/"
UPLOAD_THUMB_DIR=       "images/thumb/"
DEFAULTNOIMAGE_PATH=	"/media/hd2/sportapp/defaultthumb.png"

securityString1="ibahcbfjybingdseeegfhoodsgooppfrbaneWallaetdfwalladdOoortingrtektangdfsfhahuhrtdd"
securityString2="OfrAAddFFFERanodfseWalFORZAINTERgdsgppdd"

#max number of people in the getpeople query
MAX_PEOPLE=		'300'

ESIT_OK=		0
ESIT_ERROR=		2
ESIT_EXIST=		1
ESIT_SECUTIRYFAULT=	-2

CMD_SENDPICTOUSR=       "sendpictousr"
CMD_REGISTERDEVICE=	"registerdevice"
CMD_SENDPUSH=		"sendpush"
CMD_LOGINFB=		"loginfb"
CMD_LOGINTWITTER=	"logintwitter"
CMD_LOGIN=		"login"
CMD_SIGNUP=		"signup"
CMD_GETUSERPIC=		"userimage"
CMD_GETUSERTHUMB=       "userimagethumb"
CMD_GETUSERCOVER=	"getcover"
CMD_GETUSERCOVERTHUMB=	"getcoverthumb"
CMD_GETUSERINFO=	"userinfo"
CMD_UPDATEUSER=		"updateuser"
CMD_CHANGEPASSWORD=     "changepassword_ewrewty45rtehert254rtretwerttUUUUuuu_W_INTER"
CMD_SELECTTEAM=		"selectteam"
CMD_ADDPICTURE=		"addpicture"
CMD_GETLEAGUES=		"getleagues"
CMD_GETTEAMS=		"getteams"
CMD_DOCHECKIN=		"docheckin"
CMD_GETCHECKIN=		"getcheckin"
CMD_SENDCHAT=		"sendchat"
CMD_GETCHAT=		"getchats"
CMD_GETALLCHATS=	"getallchats"

PHOTOTYPE_ANY=		1
PHOTOTYPE_PROFILE=	2
PHOTOTYPE_POST=		3
PHOTOTYPE_COVER=	4
PHOTOTYPE_CHAT=		5

CHAT_TYPECHAT=		'c'
CHAT_TYPEPICTURE=	'p'

NOTIF_TYPEFOLLOW=	'f'
NOTIF_TYPECOMMENT=	'm'
NOTIF_TYPETAUNT=	't'
NOTIF_TYPEREPOST=	'r'
NOTIF_TYPENEWS=		'e'

THUMB_PIC_W = 120 # this is the maximum width of the images
THUMB_PIC_H = 120 # this is the maximum height of the images
#ratio = 1. * THUMB_PIC_W / THUMB_PIC_H

