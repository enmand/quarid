"""
Auto join the IRC bot to some rooms
"""
from . import Plugin

class AutoJoinPlugin(Plugin): # pylint: disable=too-few-public-methods
	"""
	Auto join the bot to the channels defined in 'modules.autojoin.channels
	"""
	def join(self):
		""" Join the given list of channels """
		for channel in self.conf.get('_autojoin.channels'):
			self.bot.on(Plugin.CONNECT, self.bot.join(channel))

def register(bot, conf):
	""" register the auto join plugin with Quarid"""
	autojoin = AutoJoinPlugin(bot, conf)
	autojoin.join()
