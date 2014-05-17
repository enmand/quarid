"""
Configuration parser for our configuration format.

It probably makes sense to use one of JSON or INI based configuration, but it
was fun writing a lexer, and it was a great learning experience, so here we are.
"""

import shlex

class Config: # pylint: disable=too-few-public-methods
	"""
	IRC bot Configuration

	Configuration for the IRC bot, based on a configuration format that is not
	unlike ini.

	Configuration files have the following attributes:
		base_class.config_option_name = config_option_value

	Where `config_option_value` can be a Python type object (int, string, bool)
	and will be properly converted to that Python type.

	The `config_option_value` can also be an array, of the form:
		[value1 value2 value3 ...]
	which will be converted into a Python list.
	"""

	__lex = None
	__cfg = {}

	def __init__(self, filename):
		__file = open(filename, 'r')
		self.__lex = shlex.shlex(__file)
		self.__lex.commenters = ';'
		self.__read()

	def __read(self): # pylint: disable=too-many-branches
		"""
		Parse and lex the given input.
		"""
		prevtok = base = opt = arr = None

		# Read our first token, and start parsing them
		tok = self.__lex.get_token()
		while tok != self.__lex.eof:

			# If our current token is the class.name split
			if tok == ".":
				base = prevtok
				if base not in self.__cfg:
					self.__cfg[base] = {}
			# If our current token is is a digit
			elif tok.isdigit():
				try:
					tok = int(tok)
				except ValueError:
					tok = float(tok)
			# If our current token is a boolean
			elif tok.lower() == "true" or tok.lower() == "false":
				tok = bool(tok)

			# If our current token is a string (delimited by " on either side)
			elif tok[0] == '"' and tok[-1] == '"':
				tok = tok[1:-1]

			# If our current token is the close of an array
			if tok == "]":
				self.__cfg[base][opt] = arr
				arr = None

			# if the prevous token
			if prevtok == ".":
				opt = tok
			elif prevtok == "=":
				self.__cfg[base][opt] = tok
			elif prevtok == "[":
				arr = []

			if arr is not None:
				if prevtok is not "]":
					arr.append(tok)

			prevtok = tok
			tok = self.__lex.get_token()

	def get(self, group=None):
		""" Return a configuration option """
		if group is not None:
			if '.' in group:
				base, opt = group.split('.')
				return self.__cfg[base][opt]

			return self.__cfg[group]
		return self.__cfg

