import shlex

class Config:
	__lex = None;
	__cfg = {}

	def __init__(self, filename = "bot.cfg"):
		__file = open(filename, 'r');
		self.__lex = shlex.shlex(__file);
		self.__read()

	def __read(self):
		tok = self.__lex.get_token();
		prevtok = None;

		base = None;
		opt = None;
		arr = None;
		while tok != self.__lex.eof:
			if tok == ".":
				base = prevtok;
				if base not in self.__cfg:
					self.__cfg[base] = {};
			elif tok == "True" or tok == "False":
				tok = bool(tok);
			elif tok.isdigit():
				try:
					tok = int(tok);
				except ValueError:
					tok = float(tok);
			elif tok[0] == '"' and tok[-1] == '"':
				tok = tok[1:-1];
			elif tok == "]":
				self.__cfg[base][opt] = arr;
				arr = None;

			if prevtok == ".":
				opt = tok;
			elif prevtok == "=":
				self.__cfg[base][opt] = tok;
			elif prevtok == "[":
				arr = [];

			if arr is not None:
				if prevtok is not "[":
					arr.append(tok);



			prevtok = tok;
			tok = self.__lex.get_token();

	def get(self, group = None):
		if group is not None:
			return self.__cfg[group]
		return self.__cfg;

if __name__ == "__main__":
	cfg = Config('bot.cfg');
	print(cfg.dict());