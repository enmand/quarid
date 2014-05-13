"""
Python irc library.

These IRC libraries are used to interact with an IRC server using Python.
"""
# pylint: disable=bad-continuation
import socket
import ssl
import re
import logger
import event


class IRC: # pylint: disable=no-init
	"""
	irc.py - IRC Library

	This library should be used to interface with some type of IRC server. This
	project was initially built for use with the qpirc bot, but should be
	extendable to any case.
	"""
	__version = "v0.4.5"
	@staticmethod
	def version():
		""" Return the version of the library """
		return IRC.__version

	@staticmethod
	def factory():
		""" Return an Evented_IRC object to listen on """
		return EventedIRC()

class EventedIRC(event.Observer): # pylint: disable=too-many-public-methods
	"""
	Evented based IRC object

	Watch for events on the IRC server that the application can subscribe to, to
	preform some action on.
	"""
	__server = ''
	__nick = ''

	def __init__(self):
		super(EventedIRC, self).__init__()
		self.log = logger.Log('irc.log').logger
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error as exc:
			self.log.error("Could not connect to server: '%s'", exc)

	def __send(self, message):
		""" Send a message to the IRC server. """
		self.sock.send(bytes(message + '\r\n', 'utf8'))

	# pylint: disable=too-many-arguments
	def connect(self, host, port, nick, password="", use_ssl=False):
		""" Connect to the IRC server. """

		self.log.debug("Connecting...")
		if use_ssl == True:
			self.log.info("Using SSL connection")
			self.sock = ssl.wrap_socket(self.sock,
										ssl_version=ssl.PROTOCOL_TLSv1_2)

		try:
			self.sock.connect((host, int(port)))
			self.__send('PASS ' + password)
			self.__send('NICK ' + nick)
			self.__send('USER ' + nick + ' 8 *  :qpirc named ' + nick)
			data = self.sock.recv(4096).decode('utf8')

			luhn = data.partition('NOTICE')
			self.__server = luhn[0][1:].strip()
			self.__nick = nick

		except socket.error as exc:
			self.log.critical("Could not connect: '%s'", exc)
			return False

		self.log.debug("Connected to " + self.__server)

	def run(self):
		"""
		Run the bot, by listening to the IRC server, and parsing the requests
		that come from it, into events that can be listened to by an application
		using this library.
		"""
		while True:

			try:
				data = self.sock.recv(4096)
				try:
					data = data.decode('utf-8')
				except UnicodeDecodeError:
					data = data.decode('iso-8859-1')

			except socket.error as sexc:
				self.log.error("Could not recieve from server %s: '%s'",
					self.__server, sexc
				)

			data = data.split('\r\n')

			for message in data:
				self.log.debug("Got message: %s", message)
				if re.compile(r'^ERROR :').match(message):
					"""
					Error connecting to the server
					"""
					self.log.error("Could not connect to server: %s", message)
					self.sock.close()
					return

				elif re.compile(r'PING(.*)').match(message):
					response = re.compile(r'PING(.*)').match(message).groups()
					"""
					Got PING, sending PONG
					"""
					self.pong(response)

				elif re.compile(r'^:%s \d{3}' % self.__server).match(message):
					serv_event, serv_data = re.compile(
						r'^:%s (\d{3}) \w* (.*)' % self.__server
					).match(message).groups()
					self.send(serv_event, serv_data)

				elif re.compile(
					r'^:(.*)!(.*)@(.*) (\w*) (.*?) :(.*)'
				).match(message):
					"""
					This is a user message
					"""
					serv_nick, serv_user, serv_host, serv_how, serv_who,\
						serv_what = re.compile(
							r'^:(.*)!(.*)@(.*) (\w*) (.*?) :(.*)'
					).match(message).groups()

					if self.__nick != serv_nick: # We aren't messaging ourselves, are we?
						self.send(serv_how, {
							'from': serv_nick,
							'user': serv_user,
							'host': serv_host,
							'how' : serv_how,
							'who' : serv_who,
							'what': serv_what
						})

	def _getname(self):
		""" Return the client's name """
		return self.__nick

	"""
	From here on out, it's server commands
	"""
	###SERVER COMMANDS###
	def nick(self, nick):
		""" Change the NICK of the client """
		self.__send('NICK %s' % nick)

	def oper(self, user, password):
		""" Identify the client as an operator """
		self.__send('OPER %s %s' % (user, password))

	def quit(self, msg):
		""" Have the client quit the IRC server """
		self.__send('QUIT :%s' % msg)

	def pong(self, response):
		""" Return a PONG respons to the server """
		self.__send('PONG%s' % response)

	###CHANNEL COMMANDS###
	def join(self, chans, keys=None):
		""" Have the client join a room on the IRC server """
		channels = ''
		channels = channels.join(chans).replace('#', ',#')
		channels = channels[1:]
		channel_keys = ", ".join(keys)
		self.__send('JOIN %s %s' % (channels, channel_keys))

	def part(self, *chans):
		""" Have the client leave a room on the IRC server """
		channels = ''
		channels = channels.join(chans).replace('#', ',#')
		channels = channels[1:]
		self.__send('PART %s' % channels)

	def mode(self, where, modes, opts):
		"""
		Have the client set a mode to itself/a user/the server/a chan on the IRC
		server
		"""
		self.__send('MODE %s %s %s' % (where, modes, opts))

	def topic(self, chan, topic):
		""" Havet the client change a channel topic """
		self.__send('TOPIC %s %s' % (chan, topic))

	def names(self, *chans):
		""" Return the names of the user on the channel """
		channels = ''
		channels = channels.join(chans).replace('#', ',#')
		channels = channels[1:]
		self.__send('NAMES %s' % channels)

	def list(self, *chans, serv=''):
		""" Return a list of channels on this IRC server """
		channels = ''
		channels = channels.join(chans).replace('#', ',#')
		channels = channels[1:]
		self.__send('LIST %s %s' % (channels, serv))

	def invite(self, nick, chan):
		""" Invite another user to a channel """
		self.__send('INVITE %s %s' % (nick, chan))

	def kick(self, chans, users, comment=''):
		""" Kick (forcefully remove) another client from a channel """
		channels = ''.join(chans).replace('#', ',#')
		channels = channels[1:]
		kicked_users = ''.join(users)
		kicked_users = kicked_users[1:]
		self.__send('KICK %s %s %s' % (channels, kicked_users, comment))

	### SERVER METHODS ###
	def version(self, serv=''):
		""" Return the server's version """
		self.__send('VERSION %s' % serv)

	### CHANNEL METHODS ###

	def msg(self, who, text):
		""" Send a message to a user, or a channel """
		self.__send('PRIVMSG %s :%s' % (who, text))

	###CONVIENCE METHODS###

	def action(self, who, text):
		""" Preform a /me action """
		self.__send('PRIVMSG %s :\x01ACTION %s' % (who, text))
