#!/usr/bin/python
import time
from daemon import runner
import MySQLdb
from defs import *

class App():
	def __init__(self):
        	self.stdin_path = '/dev/null'
       	 	self.stdout_path = '/dev/tty'
        	self.stderr_path = '/dev/tty'
        	self.pidfile_path =  '/tmp/foo.pid11'
        	self.pidfile_timeout = 5

    	def run(self):
        	while True:
			self.EraseWaitingPicChat()
            		time.sleep(11)
			self.EraseActiveUser()
			time.sleep(22)

	def EraseWaitingPicChat(self):
		db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
		cursor=db.cursor(MySQLdb.cursors.DictCursor)
                sql="UPDATE ChatLog SET Message='' WHERE SendTime<(NOW()-INTERVAL 2 MINUTE) AND Message='afsjktirntly845kfhtk594jrtjh49lrtj4955555555klrktlrjkkjhhjkhgjhcom.antoniotari.glober.waiting_image';"
                try:
                        cursor.execute(sql)
                        db.commit()
                except:
                        db.rollback()
                finally:
                        cursor.close()
			db.close()

	def EraseActiveUser(self):
		db=MySQLdb.connect(HOST,DBUSER,DBPASS,DBNAME)
                cursor=db.cursor(MySQLdb.cursors.DictCursor)
                sql="DELETE FROM ActiveUser WHERE LastPing<(NOW()-INTERVAL 5 MINUTE);"
                try:
                        cursor.execute(sql)
                        db.commit()
                except:
                        db.rollback()
                finally:
                        cursor.close()
                        db.close()

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

#Note that you'll need the python-deaemon library. In Ubuntu, you would:
#sudo apt-get install python-daemon
#Then just start it with ./howdy.py start, and stop it with ./howdy.py stop.
