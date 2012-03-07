#!/usr/bin/env python3
import irc
import config
import module

import os
import sys
import signal
import atexit
import argparse


def main():
	parser = argparse.ArgumentParser(description = "qpirc (Quard Python IRC) bot: version %s" % irc.IRC.version(),
									 epilog="Visit http://github.com/enmand/quarid for more information");
	parser.add_argument("--version", action="version", version="%s" % irc.IRC.version())
	parser.add_argument("--config", "-c", default="bot.cfg", help="Configuration file to use (default bot.cfg");
	parser.add_argument("action", choices=["start", "stop", "reload"]);
	args = parser.parse_args()

	if args.action == "start":
		start(args.config);
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
		sys.stderr.write("Failed for background process... exiting. (got %s)\n" % e.strerr);
		sys.exit(1)

	os.chdir('.')
	os.setsid();
	os.umask(0);

	try:
		if os.fork() > 0: # avoid zombie processes
			sys.exit(0); # close the second child
	except OSError as e:
		sys.stderr.write("Failed for background process... exiting. (got %s)\n" % e.strerr);
		sys.exit(1);

	atexit.register(rmpid)

	open('qpirc.pid', 'w+').write("%s" % os.getpid());


"""
Start the bot, and write the pid
"""
def start(cfg_file):
	# Do we have a pid (i.e. is the bot running?)
	try:
		fd = open('qpirc.pid', 'r');
		pid = fd.read();
		fd.close()
	except Exception:
		pid = None;

	if pid:
		sys.stderr.write("We're already running as %s\n" % pid);
		sys.exit(1);

	deamon();
	qpirc(cfg_file);

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
		sys.stderr.write("No pidfile found -- are you sure it's running?\n");
		rmpid();
		sys.exit(0);

	try:
		os.kill(pid, signal.SIGTERM);
	except OSError:
		sys.stderr.write("Couldn't terminate the process -- is it running?\n")
		rmpid();
	rmpid();

"""
Start the bot, register it's modules and run the main loop
"""
def qpirc(cfg_file):
	conf = config.Config(cfg_file)
	bot = irc.IRC.factory()

	core = conf.get('irc');
	
	bot.connect(core['host'], core['port'], core['nick'], core['pass'], conf.get('ssl')['use'])
	bot.run();

"""
Delete the pidfile (if it exists)
"""
def rmpid():
	if os.path.exists('qpirc.pid'):
		os.remove('qpirc.pid');




if __name__ == "__main__":
	main()
