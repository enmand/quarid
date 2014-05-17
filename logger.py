""" IRC library logging """
# pylint: disable=bad-continuation
import logging

class Log: # pylint: disable=too-few-public-methods
	""" Log class for getting our logger, and structring our logger file """
	def __init__(self, file_name="irc.log"):
		self.logger = logging.getLogger('irc')
		handle = logging.FileHandler("log/" + file_name)
		log_format = logging.Formatter(
			'%(asctime)s (%(name)s) %(levelname)s: %(message)s'
		)
		handle.setFormatter(log_format)
		self.logger.addHandler(handle)
		self.logger.setLevel(logging.DEBUG)
