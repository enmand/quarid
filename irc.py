import socket
import ssl
import re
import logger
import event
"""
irc.py - IRC Library

This library should be used to interface with some type of IRC server. This
project was initially built for use with the qpirc bot, but should be extendable 
to any case.
"""
class IRC:
	__version = "v0.1a"
	@staticmethod
	def version():
		return IRC.__version;

	@staticmethod
	def factory():
		return Evented_IRC();

class Evented_IRC(event.Observer):
	__server = '';
	__nick = '';

	def __init__(self):
		self.log = logger.Log('irc.log').Logger()
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error as e:
			print(e)

	def __send(self, message):
		self.sock.send(bytes(message + '\r\n', 'utf8'))

	def connect(self, host, port, nick, password="", use_ssl=False):
		self.log.debug("Connecting...")
		if(use_ssl == "True"):
			self.log.info("Using SSL connection")
			self.sock = ssl.wrap_socket(self.sock, ssl_version="TLSv1")

		try:
			self.sock.connect((host, int(port)))
			self.__send('PASS ' + password)
			self.__send('NICK ' + nick)
			self.__send('USER ' + nick + ' 8 *  :qpirc named ' + nick)
			data = self.sock.recv(4096).decode('utf8')

			luhn = data.partition('NOTICE')
			self.__server = luhn[0][1:].strip()
			self.__nick = nick;

		except socket.error as e:
			self.log.critical("Could not connect")
			print(e)
		self.log.debug("Connected to " + self.__server)

		if(use_ssl == "True"):
			print(self.sock.getpeercert());	

	def run(self):
		while True:
			try:
				data = self.sock.recv(4096).decode('utf8')
				if not data:
					break;
			except socket.error as se:
				self.log.error("Could not recieve from server " + self.__server)
				return

			data = data.split('\r\n')
			
			for m in data:
				self.log.debug(m)
				if re.compile(r'^ERROR :').match(m):
					"""
					Error connecting to the server
					"""
					self.log.error("Could not connect to server: " + m)
					self.sock.close()
					return

				elif re.compile(r'PING(.*)').match(m):
					response = re.compile(r'PING(.*)').match(m).groups();
					"""
					Got PING, sending PONG
					"""
					self.pong(response);

				elif re.compile(r'^:%s \d{3}' % self.__server).match(m):
					mEvent, mData = re.compile(r'^:%s (\d{3}) \w* (.*)' % self.__server).match(m).groups();
					self.send(mEvent, mData);
					"""
					This is a server message
					"""
					pass

				elif re.compile(r'^:(.*)!(.*)@(.*) (\w*) (.*?) :(.*)').match(m):
					"""
					This is a user message
					"""
					mNick, mUser, mHost, mHow, mWho, mWhat = re.compile(r'^:(.*)!(.*)@(.*) (\w*) (.*?) :(.*)').match(m).groups()
					if self.__nick != mNick: # We aren't messaging ourselves, are we?
						self.send(mHow, {
							'from': mNick,
							'user': mUser,
							'host': mHost,
							'how' : mHow,
							'who' : mWho,
							'what': mWhat
						});

	def _getname(self):
		return self.__nick;

	"""
	From here on out, it's server commands
	"""
	###SERVER COMMANDS###
	def nick(self, nick):
		self.__send('NICK %s' % nick)
	
	def oper(self, user, password):
		self.__send('OPER %s %s' % (user, password))
	
	def quit(self, msg):
		self.__send('QUIT :%s' % msg)

	def pong(self, response):
		self.__send('PONG%s' % response);

	###CHANNEL COMMANDS###
	def join(self, chans, keys = ()):
		cList = ''
		cList = cList.join(chans).replace('#', ',#')
		cList = cList[1:]
		kList = ''
		for k in keys:
			kList += ',' + k
			kList = kList[1:]
		self.__send('JOIN %s %s' % (cList, kList))

	def part(self, *chans):
		cList = ''
		cList = cList.join(chans).replace('#', ',#')
		cList = cList[1:]
		self.__send('PART %s' % cList)

	def mode(self, where = '', modes = '', opts = ''):
		self.__send('MODE %s %s %s' % (where, modes, opts))
	
	def topic(self, chan, topic):
		self.__send('TOPIC %s %s' % (chan, topic))

	def names(self, *chans):
		cList = ''
		cList = cList.join(chans).replace('#', ',#')
		cList = cList[1:]
		self.__send('NAMES %s' % cList)

	def list(self, *chans, serv = ''):
		cList = ''
		cList = cList.join(chans).replace('#', ',#')
		cList = cList[1:]
		self.__send('LIST %s %s' % (cList, serv))
	
	def invite(self, nick, chan):
		self.__send('INVITE %s %s' % (nick, chan))

	def kick(self, chans = (), users = (), comment = ''):
		cList = '';
		cList = cList.join(chans).replace('#', ',#')
		cList = cList[1:]
		uList = ''
		uList = uList.join(users);
		uList = uList[1:]
		self.__send('KICK %s' % (cList, uList))

	### SERVER METHODS ###
	def version(self, serv = ''):
		self.__send('VERSION %s' % serv)

	### CHANNEL METHODS ###

	def msg(self, who, text):
		self.__send('PRIVMSG %s :%s' % (who, text));

	###CONVIENCE METHODS###

	def action(self, who, text):
		self.__send('PRIVMSG %s :\x01ACTION %s' % (who, text));