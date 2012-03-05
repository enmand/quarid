import configparser

class Config:
	def __init__(self):
		self.cfg_file = configparser.ConfigParser()
		self.cfg_file.read('bot.cfg')

	def dict(self):
		cfg = dict()
		for s in self.cfg_file.sections():
			cfg[s] = dict()
			for o in self.cfg_file.options(s):
				cfg[s][o] = self.cfg_file.get(s, o)

		return cfg
