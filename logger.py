import logging

class Log:

	__logLevel = logging.DEBUG
	
	def __init__(self, file):
		self.l = logging.getLogger('irc')
		handle = logging.FileHandler("log/" + file)
		format = logging.Formatter('%(asctime)s (%(name)s) %(levelname)s: %(message)s')
		handle.setFormatter(format)
		self.l.addHandler(handle)
		self.l.setLevel(self.__logLevel)

	def Logger(self):
		return self.l
