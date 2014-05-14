"""
URLGet module for Quarid
"""
from . import Plugin

class URLGetPlugin(Plugin): # pylint: disable=too-few-public-methods
	"""
	Get statistics about a URL sent to the channel
	"""

def register(bot, conf):
	""" Register the 'urlget' module with Quarid"""
	URLGetPlugin(bot, conf)
