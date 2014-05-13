#!/usr/bin/env python3
""" The Quarid IRC bot """
# pylint: disable=bad-continuation
import argparse
import atexit
import config
import importlib
import os
import sys
import signal

from irc import IRC
from logger import Log

def main():
	""" Main callable for running Quarid """
	parser = argparse.ArgumentParser(
		description="qpirc (Quard Python IRC) bot: version %s" % (
			IRC.version()
		),
		epilog="See http://github.com/enmand/quarid for information"
	)

	parser.add_argument("--version",
		action="version", version="%s" % IRC.version()
	)

	parser.add_argument("--config", "-c",
		default="bot.cfg",
		help="Configuration file to use (default bot.cfg"
	)

	parser.add_argument("action",
		choices=["start", "stop", "reload", "debug"]
	)
	args = parser.parse_args()

	if args.action == "start":
		start(args.config)
	elif args.action == "stop":
		stop()
	elif args.action == "reload":
		print("Not yet implemented")
	elif args.action == "debug":
		start(args.config, debug=True)


def deamon():
	"""
	Background a process of the bot, so we don't have a controlling tty,
	and don't exit unexpectedly
	"""
	def _do_fork():
		""" Fork the process off to daemonize """
		try:
			if os.fork() > 0:
				sys.exit(0) #close the parent
		except OSError as exc:
			sys.stderr.write(
				"Failed to background process. Exiting. (got %s)\n" % exc)
			sys.exit(1)

	_do_fork()
	os.chdir('.')
	os.setsid()
	os.umask(0)
	_do_fork() # daemonize

	atexit.register(rmpid)
	open('qpirc.pid', 'w+').write("%s" % os.getpid())

def start(cfg_file, debug=False):
	"""
	Start the bot, and write the pid
	"""
	# Do we have a pid (i.e. is the bot running?)
	try:
		with open('qpirc.pid', 'r') as fd: # pylint: disable=invalid-name
			pid = fd.read()

			if pid:
				sys.stderr.write("We're already running as %s\n" % pid)
				sys.exit(1)
	except FileNotFoundError:
		pass

	if not debug:
		deamon()

	qpirc(cfg_file)

def stop():
	""" Stop the bot completely """
	try:
		with open('qpirc.pid', 'r') as fd: # pylint: disable=invalid-name
			pid = int(fd.read())
	except FileNotFoundError:
		sys.stderr.write("No pidfile found -- are you sure it's running?\n")
		rmpid()
		sys.exit(0)


	try:
		os.kill(pid, signal.SIGTERM)
	except OSError:
		sys.stderr.write("Couldn't terminate the process -- is it running?\n")

	rmpid()

def qpirc(cfg_file):
	"""
	Start the bot, register it's modules and run the main loop
	"""
	conf = config.Config(cfg_file)
	bot = IRC.factory()
	bot.also(conf) # also send conf with each Observer event
	core = conf.get('irc')

	for module in conf.get('modules.enabled'):
		Log('plugins.log').logger.debug('Registering plugin %s', module)

		plugin_module = importlib.import_module("plugins.%s" % module)
		plugin_module.register(bot, conf)

	bot.connect(core['host'], core['port'], core['nick'], core['pass'],
				conf.get('ssl')['use'])
	bot.run()

def rmpid():
	"""
	Delete the pidfile (if it exists)
	"""
	if os.path.exists('qpirc.pid'):
		os.remove('qpirc.pid')

if __name__ == "__main__":
	main()
