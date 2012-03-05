#!/usr/bin/env python3
import irc
import config
import os
import sys
import signal
import atexit
import argparse


def main():
	parser = argparse.ArgumentParser(description = "qpirc (Quard Python IRC) bot: version %s" % irc.IRC.version(),
									 epilog="Visit http://github.com/enmand/qpirc for more information");
	parser.add_argument("--version", action="version", version="%s" % irc.IRC.version())
	parser.add_argument("action", choices=["start", "stop", "reload"]);
	args = parser.parse_args()
	if args.action == "start":
		start();
	elif args.action == "stop":
		stop();
	elif args.action == "reload":
		print ("Not yet implemented")

"""
Background a process of the bot, so we don't have a controlling tty,
and don't exit unexpectedly
"""
def deamon():
	try:
		if os.fork() > 0:
			sys.exit(0) #close the parent
	except OSError as e:
		sys.stderr.write("Failed for background process... exiting. (got %s)" % e.strerr);
		sys.exit(1)

	os.chdir('.')
	os.setsid();
	os.umask(0);

	try:
		if os.fork() > 0: # avoid zombie processes
			sys.exit(0); # close the second child
	except OSError as e:
		sys.stderr.write("Failed for background process... exiting. (got %s)" % e.strerr);
		sys.exit(1);

	atexit.register(rmpid)

	open('qpirc.pid', 'w+').write("%s" % os.getpid());


"""
Start the bot, and write the pid
"""
def start():
	# Do we have a pid (i.e. is the bot running?)
	try:
		fd = open('qpirc.pid', 'r');
		pid = fd.read();
		fd.close()
	except Exception:
		pid = None;

	if pid:
		sys.stderr.write("We're already running as %s" % pid);
		sys.exit(1);

	deamon();
	qpirc();

"""
Close the bot
"""
def stop():
	try:
		fd = open('qpirc.pid', 'r');
		pid = int(fd.read());
		fd.close();
	except Exception:
		pid = None;

	if not pid:
		sys.stderr.write("No pidfile found -- are you sure it's running?");
		rmpid();
		os.exit(0);

	try:
		os.kill(pid, signal.SIGTERM);
	except OSError:
		sys.stderr.write("Couldn't terminate the process -- is it running?")
		rmpid();
	rmpid();

"""
Start the bot, register it's modules and run the main loop
"""
def qpirc():
	conf = config.Config().dict()
	bot = irc.IRC.factory()

	## HERE IS WHERE WE WANT TO ADD SOME MODULES

	bot.addListener('376', printAndJoin);
	bot.addListener('privmsg', do_something)


	core = conf['core']
	bot.connect(core['host'], core['port'], core['nick'], core['pass'], conf['ssl']['use_ssl'])
	bot.run();

"""
Delete the pidfile (if it exists)
"""
def rmpid():
	if os.path.exists('qpirc.pid'):
		os.remove('qpirc.pid');


def printAndJoin(bot, server):
	bot.join("#qpirc");
	bot.msg("#qpirc", "I work!");


def do_something(bot, got):
	print(repr(got));
	if(got['what'][0] == "!"):
		action = got['what'][1:];
		if action == "quit":
			bot.quit("Thanks for having me!");
		if action == "slap":
			bot.action(got['who'], 'slaps enmand %s' % got['from']);
	if(got['who'] != bot._getname()):
		bot.msg(got['who'], "Whoo!")
	else:
		bot.msg(got['from'], "Good!");



if __name__ == "__main__":
	main()