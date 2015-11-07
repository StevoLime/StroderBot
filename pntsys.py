import urllib2
import json
import time
import sqlite3
import ConfigParser

conpar = ConfigParser.SafeConfigParser()
conpar.read('botvar.ini')

owner = conpar.get("channelinfo", "owner")
userpointsv = conpar.get("points", "viewerpoints")
userpoints = int(userpointsv)					
modpointsv = conpar.get("points", "modpoints")
modpoints = int(modpointsv)					
staffpointsv = conpar.get("points", "staffpoints")
staffpoints = int(staffpointsv)					
btimer = conpar.get("timer", "bottimer")						
bottimer = int(btimer)


def pointsys():

	twconn = sqlite3.connect('points.db')
	twcur = twconn.cursor()

	twapi = 'https://tmi.twitch.tv/group/user/%s/chatters' % owner
	#print tdapi
	twresponse = urllib2.urlopen(twapi)
	twapiinfo = json.load(twresponse)
	
	twmods = twapiinfo["chatters"]["moderators"]
	twviewers = twapiinfo["chatters"]["viewers"]
	twstaff = twapiinfo["chatters"]["staff"]
	twadmins = twapiinfo["chatters"]["admins"]
	twgmods = twapiinfo["chatters"]["global_mods"]
	twfullstaff = twstaff + twadmins + twgmods
	
	modmax = len(twmods)
	modcount = modmax - 1
	modcur = 0
	
	viewmax = len(twviewers)
	viewcount = viewmax - 1
	viewcur = 0
	
	staffmax = len(twfullstaff)
	staffcount = staffmax - 1
	staffcur = 0
	
	while(1):
		#mods
		if modcur <= modcount:

			modlistuser = twmods[modcur]
			modsql = 'SELECT * FROM Users WHERE username="%s"' % (modlistuser)
			#ucur.execute("SELECT * FROM Users WHERE username = ?;",(ulistuser,))
			twcur.execute(modsql)
			moddbuser = twcur.fetchone()
			print moddbuser
		
			if moddbuser == None:
				twcur.execute("INSERT INTO Users VALUES(?, ?, ?);", (modlistuser, modpoints, modpoints))
				print "User %s added." % twmods[modcur]
				
				modcur = modcur + 1

			else:	
				twcur.execute("UPDATE Users SET current = current + ?, total = total + ? WHERE username = ?;", (modpoints, modpoints, modlistuser))
				print "Added points to %s" % twmods[modcur]
				
				modcur = modcur + 1
		
		#staff
		elif staffcur <= staffcount:

			stafflistuser = twfullstaff[staffcur]
			staffsql = 'SELECT * FROM Users WHERE username="%s"' % (stafflistuser)
			#ucur.execute("SELECT * FROM Users WHERE username = ?;",(ulistuser,))
			twcur.execute(staffsql)
			staffdbuser = twcur.fetchone()
			print staffdbuser
		
			if staffdbuser == None:
				twcur.execute("INSERT INTO Users VALUES(?, ?, ?);", (stafflistuser, staffpoints, staffpoints))
				print "User %s added." % twfullstaff[staffcur]
				
				staffcur = staffcur + 1

			else:	
				twcur.execute("UPDATE Users SET current = current + ?, total = total + ? WHERE username = ?;", (staffpoints, staffpoints, stafflistuser))
				print "Added points to %s" % twfullstaff[staffcur]
				
				staffcur = staffcur + 1
				
		#viewers
		elif viewcur <= viewcount:

			viewerlistuser = twviewers[viewcur]
			viewersql = 'SELECT * FROM Users WHERE username="%s"' % (viewerlistuser)
			#ucur.execute("SELECT * FROM Users WHERE username = ?;",(ulistuser,))
			twcur.execute(viewersql)
			viewerdbuser = twcur.fetchone()
			print viewerdbuser
		
			if viewerdbuser == None:
				twcur.execute("INSERT INTO Users VALUES(?, ?, ?);", (viewerlistuser, userpoints, userpoints))
				print "User %s added." % twviewers[viewcur]
				
				viewcur = viewcur + 1

			else:	
				twcur.execute("UPDATE Users SET current = current + ?, total = total + ? WHERE username = ?;", (userpoints, userpoints, viewerlistuser))
				print "Added points to %s" % twviewers[viewcur]
				
				viewcur = viewcur + 1
	
		elif viewcur > viewcount:

			twconn.commit()
			time.sleep(bottimer)
			
			twresponse = urllib2.urlopen(twapi)
			twapiinfo = json.load(twresponse)
			
			twmods = twapiinfo["chatters"]["moderators"]
			twviewers = twapiinfo["chatters"]["viewers"]
			twstaff = twapiinfo["chatters"]["staff"]
			twadmins = twapiinfo["chatters"]["admins"]
			twgmods = twapiinfo["chatters"]["global_mods"]
			twfullstaff = twstaff + twadmins + twgmods
			
			modmax = len(twmods)
			modcount = modmax - 1
			modcur = 0
	
			viewmax = len(twviewers)
			viewcount = viewmax - 1
			viewcur = 0
	
			staffmax = len(twfullstaff)
			staffcount = staffmax - 1
			staffcur = 0