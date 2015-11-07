#Twitch chat bot code by Steven Anderson.
#Code is written in Python and is still being developed.
#If you use this code for a chat bot, please only change the variables that you need to change.
#If you want to add/remove commands and do not understand Python, please ask Steven.
#Each section of the code should have comments saying what it is.

#Importing modules for code.
import socket
import time
import re
import select
import requests
import urllib2
import json
import yaml
import thread
import threading
import sqlite3
import os
import ConfigParser
import pntsys
import pushbullet
import random

#Importing variables file
conpar = ConfigParser.SafeConfigParser()
conpar.read('botvar.ini')

#Variables for bot. Text needs to be in ' ' but numbers do not.
#Variables needing to be modified should be located in the botvar.ini file.

server = 'irc.twitch.tv'						
port = 443										
nick = conpar.get("botname", "nick")							
oauth = conpar.get("botname", "oauth")							
channel = conpar.get("channelinfo", "channel")						
owner = conpar.get("channelinfo", "owner")							
userpointsv = conpar.get("points", "viewerpoints")
userpoints = int(userpointsv)					
modpointsv = conpar.get("points", "modpoints")
modpoints = int(modpointsv)					
staffpointsv = conpar.get("points", "staffpoints")
staffpoints = int(staffpointsv)			
btimer = conpar.get("timer", "bottimer")						
bottimer = int(btimer)
pntname = conpar.get("commands", "pntname")
pntvalu = conpar.get("commands", "pntval")
pntval = int(pntvalu)
compntreqv = conpar.get("commands", "compntreq")
compntreq = int(compntreqv)
api_key = conpar.get("pbullet", "apikey")
notiov = conpar.get("pbullet", "notifications")
notio = int(notiov)
devnumv = conpar.get("pbullet", "devnumb")
devnum = int(devnumv)
pb = pushbullet.Pushbullet(api_key)
winph = pb.devices[devnum]
tarptime = time.time()
latetime = time.time()
hitime = time.time()
byetime = time.time()
cwtime = time.time()
waittime = 30
tarpwait = 10
vkact = 1
vkee = "nub"
vklistlen = 0
latsass = 0
rafact = 1
rdb = None
vernum = '1.0a'

#Connecting to Twitch irc server.
s = socket.socket()
s.connect((server, port))
s.send("PASS %s\r\n" % (oauth))
s.send("NICK %s\r\n" % nick)
s.send("USER %s\r\n" % (nick))
s.send("CAP REQ :twitch.tv/membership \r\n")
s.send("JOIN %s\r\n" % channel)

print "Connected to channel %s" % channel


#Function to check if the point database is there and create if necessary.
def dbexists():

	if os.path.exists('points.db'):
		print "Database is there."
		
	else:
		conn = sqlite3.connect('points.db')
		cur = conn.cursor()
		cur.execute("CREATE TABLE Users(username TEXT, current INT, total INT)")

		conn.commit()
		conn.close()
		print "Created Database"

#Run point database check.
dbexists()

#Connect to point database
lconn = sqlite3.connect('points.db')
lcur = lconn.cursor()

#Function to check if command database is there and create if necessary.
def comdbexists():

	if os.path.exists('custcoms.db'):
		print "Coms Database is there."
		
	else:
		comdbconn = sqlite3.connect('custcoms.db')
		comdbcur = comdbconn.cursor()
		comdbcur.execute("CREATE TABLE Comsdb(com TEXT, lvl TEXT, commsg TEXT)")

		comdbconn.commit()
		comdbconn.close()
		print "Created Coms Database"

#Run command database check.
comdbexists()

#Connect to command database
comconn = sqlite3.connect('custcoms.db')
comcur = comconn.cursor()


print "Bot Started"

#Twitch api array pull. modlist is for mod commands. comuser is for command user. modlistd, userlist, and tstafflist is for the Point System.
def modlist():
	tapi = 'https://tmi.twitch.tv/group/user/%s/chatters' % owner
	response = urllib2.urlopen(tapi)
	tapiinfo = yaml.load(response)
	return tapiinfo["chatters"]["moderators"]

def modlistd():
	tdapi = 'https://tmi.twitch.tv/group/user/%s/chatters' % owner
	dresponse = urllib2.urlopen(tdapi)
	tdapiinfo = json.load(dresponse)
	return tdapiinfo["chatters"]["moderators"]
	
def userlist():
	tuapi = 'https://tmi.twitch.tv/group/user/%s/chatters' % owner
	uresponse = urllib2.urlopen(tuapi)
	tuapiinfo = json.load(uresponse)
	return tuapiinfo["chatters"]["viewers"]
	
def tstafflist():
	tsapi = 'https://tmi.twitch.tv/group/user/%s/chatters' % owner
	tsresponse = urllib2.urlopen(tsapi)
	tsapiinfo = json.load(tsresponse)
	
	stafflist = tsapiinfo["chatters"]["staff"]
	adminslist = tsapiinfo["chatters"]["admins"]
	gmodslist = tsapiinfo["chatters"]["global_mods"]
	
	combinedlist = stafflist + adminslist + gmodslist
	return combinedlist

def comuser():
	complete = msg[1: ].split(":", 1) # Parse the message into useful data sender[0] is username
	info = complete[0].split(" ")
	msgpart = complete[1]
	sender = info[0].split("!")
	return sender[0]

#Point System start
psys = threading.Thread(target = pntsys.pointsys)
psys.start()

#Setup for raffle system
vkconn = sqlite3.connect(':memory:')
vkcur = vkconn.cursor()


#Commands for bot. Do not change, remove, or add unless you understand the command setup.
#Custom commands can be added or removed using the addcomd and delcomd commands respectfully.
while(1):
	msg = s.recv(1024)
	#print msg
	
	if msg.find('PING') != -1:
		s.send('PONG ' + msg.split()[1] + '\r\n')

	if msg.find('PRIVMSG') != -1:
		tmp = msg.split('PRIVMSG')[-1]
		
		if tmp.find('!') != -1:
			regex = re.compile("(!\S*)")
			r = regex.findall(tmp)
			#check com database
			comr = r[0]
			comdbr = 'SELECT * FROM Comsdb WHERE com="%s"' % comr
			comcur.execute(comdbr)
			comdbf = comcur.fetchone()
			if comdbf is not None:
				rdb = comdbf[0]
				#print rdb
			for i in r:
				if i == '!notice':
					if comuser() == 'stevolime':
						s.send("PRIVMSG %s :Senpai noticed me!\r\n" % channel)
				
				#bot info
				elif i == "!version":
					s.send("PRIVMSG %s :Version %s. Written in Python.\r\n" % (channel, vernum))
				elif i == "!botinfo":
					s.send("PRIVMSG %s :This bot is using the StroderBot software in development by StevoLime using python and is on Version %s.\r\n" % (channel, vernum))
				elif i == "!loyinfo":
					s.send("PRIVMSG %s :If you would like to know your points use !my%ss. Mods can also run !%ss for %s values and timer.\r\n" % (channel, pntname, pntname, pntname))
				
				#some fun commands
				elif i == "!fun":
					s.send("PRIVMSG %s :!powers and !random\r\n" % channel)	
				
				#point system commands
				elif i == "!my%ss" % pntname:
					lcuser = comuser()
					lsql = 'SELECT * FROM Users WHERE username="%s"' % (lcuser)
					lcur.execute(lsql)
					lcuserd = lcur.fetchone()
					if lcuserd != None:
						s.send("PRIVMSG %s :%s currently has %s %ss and has earned a total of %s %ss.\r\n" % (channel, comuser(), lcuserd[1], pntname, lcuserd[2], pntname))
					else:
						s.send("PRIVMSG %s :%s currently has no %ss.\r\n" % (channel, comuser(), pntname))
				elif i == "!%ss" % pntname:
					if comuser() in modlist():
						s.send("PRIVMSG %s :%s values are currently %s for mods and %s for viewers every %s seconds.\r\n" % (channel, pntname.capitalize(), modpoints, userpoints, bottimer))
				elif i == "!%scheck" % pntname:
					if comuser() in modlist():
						tregex = re.compile("(!\S*\s\S*)")
						tr = tregex.findall(tmp)
						trs = tr[0]
						trsplit = trs.split()
#update dingbot with this code for point check						
						if len(trsplit) == 2:
							lsql = 'SELECT * FROM Users WHERE username="%s"' % (trsplit[1])
							lcur.execute(lsql)
							lcuserd = lcur.fetchone()
						
							if lcuserd != None:
								s.send("PRIVMSG %s :%s currently has %s %ss and has earned a total of %s %ss.\r\n" % (channel, trsplit[1], lcuserd[1], pntname, lcuserd[2], pntname))
							else:
								s.send("PRIVMSG %s :%s currently has no %ss.\r\n" % (channel, trsplit[1], pntname))	
						else:
							s.send("PRIVMSG %s :Please specify a user.\r\n" % channel)
								
				elif i == "!give%ss" % pntname:
					if comuser() == owner:
						tregex = re.compile("(!\S*\s\S*\s\S*)")
						tr = tregex.findall(tmp)
						trs = tr[0]
						trsplit = trs.split()
						if len(trsplit) == 3:
							trpnt = trsplit[2]
						
							if trpnt.isdigit():
						
								lsql = 'SELECT * FROM Users WHERE username="%s"' % (trsplit[1])
								lcur.execute(lsql)
								lcuserd = lcur.fetchone()
							
								if lcuserd == None:
									lcur.execute("INSERT INTO Users VALUES(?, ?, ?);", (trsplit[1], trsplit[2], trsplit[2]))
									lconn.commit()
									s.send("PRIVMSG %s :%s gave %s %s %ss.\r\n" % (channel, owner, trsplit[1], trsplit[2], pntname))
								else:
									lcur.execute("UPDATE Users SET current = current + ?, total = total + ? WHERE Username = ?;", (trsplit[2], trsplit[2], trsplit[1]))
									lconn.commit()
									s.send("PRIVMSG %s :%s gave %s %s %ss.\r\n" % (channel, owner, trsplit[1], trsplit[2], pntname))
								
							else:
								s.send("PRIVMSG %s :%s is not a number. Try again.\r\n" % (channel, trsplit[2]))
						else:
							s.send("PRIVMSG %s :Not enough info. Please try again. !give%ss <username> <points> \r\n" % (channel, pntname))
							
				elif i == "!take%ss" % pntname:
					if comuser() == owner:
						tapregex = re.compile("(!\S*\s\S*\s\S*)")
						tapr = tapregex.findall(tmp)
						taprs = tapr[0]
						taprsplit = taprs.split()
						if len(taprsplit) == 3:
							taprpnt = taprsplit[2]
						
							if taprpnt.isdigit():
						
								lsql = 'SELECT * FROM Users WHERE username="%s"' % (taprsplit[1])
								lcur.execute(lsql)
								lcuserd = lcur.fetchone()
							
								lcuint = int(lcuserd[1])
								tapint = int(taprpnt)
							
								if lcuserd == None:
									s.send("PRIVMSG %s :%s has no %ss.\r\n" % (channel, taprsplit[1], pntname))
								else:
									if tapint >= lcuint:
										tapuser = taprsplit[1]
										#print tapuser
										tapsql = 'UPDATE Users SET current=0, total=total WHERE username="%s"' % (tapuser)
										lcur.execute(tapsql)
										#lcur.execute("UPDATE Users SET current = 0, total = total WHERE Username = ?;", tapuser)
										lconn.commit()
										s.send("PRIVMSG %s :%s took all %s from %s.\r\n" % (channel, owner, pntname, taprsplit[1]))
								
									else:
										lcur.execute("UPDATE Users SET current = current - ? WHERE Username = ?;", (taprsplit[2], taprsplit[1]))
										lconn.commit()
										s.send("PRIVMSG %s :%s took from %s %s %ss.\r\n" % (channel, owner, taprsplit[1], taprsplit[2], pntname))
								
							else:
								s.send("PRIVMSG %s :%s is not a number. Try again.\r\n" % (channel, taprsplit[2]))
						else:
							s.send("PRIVMSG %s :Not enough info. Please try again. !take%ss <username> <points> \r\n" % (channel, pntname))
						
				elif i == "!giveall":
					if comuser() in modlist():
						tregex = re.compile("(!\S*\s\S*)")
						tr = tregex.findall(tmp)
						trs = tr[0]
						trsplit = trs.split()
						if len(trsplit) == 2:
							trpnt = trsplit[1]
						
							if trpnt.isdigit():
						
								listall = modlistd() + userlist() + tstafflist()
								allmax = len(listall)
								allcount = allmax - 1
								allcur = 0
						
								s.send("PRIVMSG %s :Giving everyone %s %ss. Please wait.\r\n" % (channel, trsplit[1], pntname))
						
								while allcur <= allcount:
									listalluser = listall[allcur]
									lsql = 'SELECT * FROM Users WHERE username="%s"' % (listalluser)
									lcur.execute(lsql)
									lcuserd = lcur.fetchone()
		
									if lcuserd == None:
										lcur.execute("INSERT INTO Users VALUES(?, ?, ?);", (listalluser, trsplit[1], trsplit[1]))
										print "User %s added." % listalluser
										allcur = allcur + 1
										lconn.commit()
			
									else:
										lcur.execute("UPDATE Users SET current = current + ?, total = total + ? WHERE Username = ?;", (trsplit[1], trsplit[1], listalluser))
										print "Added points to %s" % listalluser
										allcur = allcur + 1
										lconn.commit()
						
								s.send("PRIVMSG %s :Everyone was given %s %ss.\r\n" % (channel, trsplit[1], pntname))
						
							else:
								s.send("PRIVMSG %s :%s is not a number. Try again.\r\n" % (channel, trsplit[1]))
						else:
							s.send("PRIVMSG %s :Not enough info. Please try again. !giveall <points> \r\n" % channel)
				
				#fun commands
				elif i == "!powers":
				
					powuser = comuser()
					powsql = 'SELECT * FROM Users WHERE username="%s"' % (powuser)
					lcur.execute(powsql)
					powuserd = lcur.fetchone()
					
					powurl = 'http://unitinggamers.com/twitch/php/powers.php'
					powresponse = urllib2.urlopen(powurl)
					powresp = yaml.load(powresponse)
					
					if powuserd[pntval] >= compntreq:
						s.send("PRIVMSG %s :%s has the power of %s.\r\n" % (channel, powuser, powresp))
						time.sleep(10)
				
				
				
				elif i == "!tarp":
					if (time.time() - tarptime) >= tarpwait:
						tarpuser = comuser()
						tarp = random.randrange(1,100)
						tarptime = time.time()
						if tarp <= 90:
							s.send("PRIVMSG %s :/timeout %s 1\r\n" % (channel, tarpuser))
							s.send("PRIVMSG %s :%s has been placed into the bloody sheets of the murder tarp.\r\n" % (channel, tarpuser))
						else:
							s.send("PRIVMSG %s :%s has escaped the damning folds of the murder tarp... for now.\r\n" % (channel, tarpuser))
				
				
				
				elif i == "!slap":
					if comuser() in modlist():
						
						slapuser = comuser()
						sregex = re.compile("(!\S*\s\S*)")
						sr = sregex.findall(tmp)
						srs = sr[0]
						srsplit = srs.split()
						srpnt = srsplit[1]
						ranslap = random.randrange(1, 20)
						
						if ranslap <= 10:
							s.send("PRIVMSG %s :%s has slapped the hoe %s.\r\n" % (channel, slapuser.capitalize(), srpnt.capitalize()))
						elif ranslap >= 11:
							s.send("PRIVMSG %s :%s has pimp slapped %s.\r\n" % (channel, slapuser.capitalize(), srpnt.capitalize()))
						
				#notification commands
				
				#elif i == "!notiotest":
				#	if comuser() == owner:
						
				#		print "Notifications: 1 is on, 2 is off."
				#		print notio
						#winph.push_note("Notification Settings.", "Notio is %s" % notio)
				#		s.send("PRIVMSG %s :%s, the value is %s.\r\n" % (channel, owner, notio))
				
				elif i == "!notdev":
					if comuser() == owner:
						
						print "You devices for PushBullet. Count left to right starting at 0."
						print "The number is used in the config file to set your device."
						print "Config default is 0."
						print(pb.devices)
						s.send("PRIVMSG %s :Check command window.\r\n" % channel)
				
						
				elif i == "!notify":
					if comuser() == owner:
						if notio == 1:
							notio = 2
							s.send("PRIVMSG %s :Notification commands turned off.\r\n" % channel)
							
						elif notio == 2:
							notio = 1	
							s.send("PRIVMSG %s :Notification commands turned on.\r\n" % channel)
						
				elif i == "!sayhi":
					if notio == 1:
						if (time.time() - hitime) > (waittime / 2):
						
							hitime = time.time()
							hicom = comuser()
							winph.push_note("Hey strimmer!", "%s says Hi." % hicom.capitalize())
							s.send("PRIVMSG %s :%s has told strimmer hi.\r\n" % (channel, hicom.capitalize()))
						
				elif i == "!saybye":
					if notio == 1:
						if (time.time() - byetime) > (waittime / 2):
						
							byetime = time.time()
							byecom = comuser()
							winph.push_note("Strimmer", "%s says Bye." % byecom.capitalize())
							s.send("PRIVMSG %s :%s has told strimmer bye.\r\n" % (channel, byecom.capitalize()))
						
				elif i == "!late":
					if notio == 1:
						if (time.time() - latetime) > waittime:
						
							lapi = 'https://api.twitch.tv/kraken/streams/%s' % owner
							lres = urllib2.urlopen(lapi)
							strmnfo = yaml.load(lres)

							print latsass
							#print strmnfo["stream"]
							latetime = time.time()
							if latsass == 5:
								s.send("PRIVMSG %s :/timeout %s 1\r\n" % (channel, comuser()))
								latsass = 0
							else:
								if strmnfo["stream"] == None:
							
									comun = comuser()
									winph.push_note("You are late!", "According to %s." % comun.capitalize())
									s.send("PRIVMSG %s :Hey %s, Strimmer has been notified.\r\n" % (channel, comun.capitalize()))
									latsass = latsass + 1
								else:
									s.send("PRIVMSG %s :Strimmer is here you pleb.\r\n" % channel)
									latsass = latsass + 1
				
						
				#votekick system	
				elif i == "!votekick":
					if vkact == 1:
				
						vkuser = comuser()
						vksql = 'SELECT * FROM Users WHERE username="%s"' % (vkuser)
						lcur.execute(vksql)
						vkuserd = lcur.fetchone()
						
						vkregex = re.compile("(!\S*\s\S*)")
						vkr = vkregex.findall(tmp)
						vkrs = vkr[0]
						vkrsplit = vkrs.split()					
						
						vkee = vkrsplit[1]
						
						vktwapi = 'https://tmi.twitch.tv/group/user/%s/chatters' % owner
						vktwresponse = urllib2.urlopen(vktwapi)
						vktwapiinfo = json.load(vktwresponse)
	
						vktwmods = vktwapiinfo["chatters"]["moderators"]
						vktwviewers = vktwapiinfo["chatters"]["viewers"]
						vktwstaff = vktwapiinfo["chatters"]["staff"]
						vktwadmins = vktwapiinfo["chatters"]["admins"]
						vktwgmods = vktwapiinfo["chatters"]["global_mods"]
						vktwfulllist = vktwmods + vktwviewers + vktwstaff + vktwadmins + vktwgmods
	
						vklistlen = len(vktwfulllist)
						
						if vkuserd[pntval] >= 1000:
							vkcur.execute("CREATE TABLE VoteKick(username TEXT, vote INT)")
							#yes = 1 no = 2
							vkconn.commit()
							vkuv = 1
							vkcur.execute("INSERT INTO VoteKick VALUES(?, ?);",(comuser(), vkuv))
							vkconn.commit()
							vkact = 2
							s.send("PRIVMSG %s :%s has started a votekick on %s. !f1 votes yes. !f2 votes no.\r\n" % (channel, vkuser.capitalize(), vkee))

						
						else:
							s.send("PRIVMSG %s :You can't start a votekick yet.\r\n" % channel)
					
				elif i == "!f1":
					if vkact == 2:
						vkyu = comuser()
						vkysql = 'SELECT * FROM VoteKick WHERE username="%s"' % vkyu
						vkcur.execute(vkysql)
						vkyesusercheck = vkcur.fetchone()
						if vkyesusercheck == None:
							vkuv = 1
							vkcur.execute("INSERT INTO VoteKick VALUES(?, ?);",(comuser(), vkuv))
							vkconn.commit()
							s.send("PRIVMSG %s :%s has voted yes.\r\n" % (channel, comuser()))
						
							vkonesql = 'SELECT username FROM VoteKick WHERE vote=1'
							vkcur.execute(vkonesql)
							vkcurd = vkcur.fetchall()
							vkyesnum = len(vkcurd)
							if vkyesnum >= (vklistlen / 2):
								s.send("PRIVMSG %s :/timeout %s 5\r\n" % (channel, vkee))
								vkcur.execute("DROP TABLE VoteKick;")
								vkconn.commit()
								vkact = 1
								s.send("PRIVMSG %s :Votekick on %s is successful.\r\n" % (channel, vkee))
					else:
						s.send("PRIVMSG %s :There is no votekick currently.\r\n" % (channel))
							
				elif i == "!f2":
					if vkact == 2:
						vknu = comuser()
						vknsql  = 'SELECT * FROM VoteKick WHERE username="%s"' % vknu
						vkcur.execute(vknsql)
						vknousercheck = vkcur.fetchone()
						if vknousercheck == None:
							nvkuv = 2
							vkcur.execute("INSERT INTO VoteKick VALUES(?, ?);",(comuser(), nvkuv))
							vkconn.commit()
							s.send("PRIVMSG %s :%s has voted no.\r\n" % (channel, comuser()))
						
							vktwosql = 'SELECT username FROM VoteKick WHERE vote=2'
							vkcur.execute(vktwosql)
							vkcurdt = vkcur.fetchall()
							vknonum = len(vkcurdt)
							if vknonum >= (vklistlen / 2):
								s.send("PRIVMSG %s :Votekick on %s is unsuccessful.\r\n" % (channel, vkee))
								vkcur.execute("DROP TABLE VoteKick;")
								vkconn.commit()
								vkact = 1
					else:
						s.send("PRIVMSG %s :There is no votekick currently.\r\n" % (channel))
				
				elif i == "!f3":
					if vkact == 2:
						s.send("PRIVMSG %s :Does it look like I said !f3 you scrub?\r\n" % (channel))
					
				elif i == "!f4":
					if vkact == 2:
						s.send("PRIVMSG %s :Attack! Kippa\r\n" % (channel))
						s.send("PRIVMSG %s :/timeout %s 1\r\n" % (channel, comuser()))
					
				elif i == "!f64":
					if vkact == 2:
						fuser = comuser()
						fsql = 'SELECT * FROM Users WHERE username="%s"' % (fuser)
						lcur.execute(fsql)
						lcuserd = lcur.fetchone()
						
						if lcuserd == None:
							s.send("PRIVMSG %s :I am not a Nintendo. And you now owe Nintendo your %ss.\r\n" % (channel, pntname))
						else:
							fuserp = int(lcuserd[1])
							if fuserp <= 64:
								fasql = 'UPDATE Users SET current=0, total=total WHERE username="%s"' % (fuser)
								lcur.execute(fasql)
								lconn.commit()
								s.send("PRIVMSG %s :I am not a Nintendo. And now Nintendo has taken your %ss.\r\n" % (channel, pntname))
							else:
								ftsql = 'UPDATE Users SET current = current - 64, total=total WHERE username="%s"' % (fuser)
								lcur.execute(ftsql)
								lconn.commit()
								s.send("PRIVMSG %s :I am not a Nintendo. And now Nintendo has taken 64 of your %ss.\r\n" % (channel, pntname))
					
				elif i == "!f69":
					if vkact == 2:
						s.send("PRIVMSG %s :Oh Hell No! Not in my chat! Kippa\r\n" % (channel))
						s.send("PRIVMSG %s :/timeout %s 1\r\n" % (channel, comuser()))
					
				elif i == "!vkstop":
					if comuser() in modlist():
						if vkact == 2:
							vkcur.execute("DROP TABLE VoteKick;")
							vkconn.commit()
							vkact = 1
							s.send("PRIVMSG %s :A mod has stopped the votekick.\r\n" % (channel))
				
				
				#raffle commands
				elif i == "!vwrraf":
					if comuser() in modlist():
						if rafact == 1:
							vrtwapi = 'https://tmi.twitch.tv/group/user/%s/chatters' % owner
							vrtwresponse = urllib2.urlopen(vrtwapi)
							vrtwapilist = yaml.load(vrtwresponse)
							
							vrmodsu = vrtwapilist["chatters"]["moderators"]
							vrmodsu.remove(owner)
							vrmodsu.remove(nick)
							vrstaff = vrtwapilist["chatters"]["staff"]
							vradmins = vrtwapilist["chatters"]["admins"]
							vrgmods = vrtwapilist["chatters"]["global_mods"]
							vrviewers = vrtwapilist["chatters"]["viewers"]
							vrusrlst = vrmodsu + vrstaff + vradmins + vrgmods + vrviewers
							vrlstlen = len(vrusrlst)
							if vrlstlen > 1:
								vrranmax = vrlstlen - 1
							else:
								vrranmax = vrlstlen
							vrnum = random.randrange(0,vrranmax)
							vrwin = vrusrlst[vrnum]
							vrwinapi = 'https://api.twitch.tv/kraken/users/%s/follows/channels/%s' % (vrwin, owner)
							vrwinresp = requests.get(vrwinapi)
							vrwininfo = vrwinresp.json()
							
							if "message" in vrwininfo:
								s.send("PRIVMSG %s :Raffle winner is %s, and they ARE NOT a follower. BibleThump\r\n" % (channel, vrwin))
							else:
								s.send("PRIVMSG %s :Raffle winner is %s, and they are a follower. deIlluminati\r\n" % (channel, vrwin))	
						else:
							s.send("PRIVMSG %s :Raffle is already active.\r\n" % channel)
							
				#custom commands
				elif i == "!addcomd":
					if comuser() in modlist():
						ncall = tmp.split('|')
						if len(ncall) == 4:
							nccomm = ncall[1].lstrip()
							nccom = nccomm.rstrip()
							nclvll = ncall[2].lstrip()
							nclvl = nclvll.rstrip()
							ncmsgg = ncall[3].lstrip()
							ncmsg = ncmsgg.rstrip()
		
							acomsql = 'SELECT * FROM Comsdb WHERE com="%s"' % (nccom)
							comcur.execute(acomsql)
							actest = comcur.fetchone()
		
							if actest == None:
								comcur.execute("INSERT INTO Comsdb VALUES(?, ?, ?);", (nccom, nclvl, ncmsg))
								comconn.commit()
								s.send("PRIVMSG %s :Command has been added.\r\n" % channel)
						else:
							s.send("PRIVMSG %s :Not enough info for command. Please try again.\r\n" % channel)
			
				elif i == "!delcomd":
					if comuser() in modlist():
						dcall = tmp.split('|')
						if len(dcall) == 2:
							dccn = dcall[1]
							dccomm = dccn.lstrip()
							dccom = dccomm.rstrip()
		
							dcomsql = 'SELECT * FROM Comsdb WHERE com="%s"' % (dccom)
							comcur.execute(dcomsql)
							dctest = comcur.fetchone()
		
							if dctest is not None:
								delcomsql = 'DELETE FROM Comsdb WHERE com="%s"' % (dccom)
								comcur.execute(delcomsql)
								comconn.commit()
								s.send("PRIVMSG %s :Command has been removed.\r\n" % channel)
								
						else:
							s.send("PRIVMSG %s :No command specified. Please try again.\r\n" % channel)
							
				elif i == rdb:
					comusernc = comuser()
					if comdbf is not None:
						comlvl = comdbf[1]
						if comlvl == 'ol':
							if comusernc == owner:
								s.send("PRIVMSG %s :%s\r\n" % (channel, comdbf[2]))
						elif comlvl == 'ml':
							if comusernc in modlist():
								s.send("PRIVMSG %s :%s\r\n" % (channel, comdbf[2]))
						elif comlvl == 'vl':
							s.send("PRIVMSG %s :%s\r\n" % (channel, comdbf[2]))

				