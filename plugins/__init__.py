"""
Base module for plugins
"""

class Plugin: # pylint: disable=too-few-public-methods
	"""
	Base plugin

	All plugins should subclass this classs
	"""
	CONNECT = '001'

	def __init__(self, bot, conf):
		self.bot = bot
		self.conf = conf
