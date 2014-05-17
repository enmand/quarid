"""
Slap module for Quarid
"""
from . import Plugin

class SlapPlugin(Plugin): # pylint: disable=too-few-public-methods
	""" SlapPlugin class, for doing slap commands """

def register(bot, conf):
	""" Register the 'slap' module with Quarid """
	SlapPlugin(bot, conf)
