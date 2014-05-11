"""
Event management system

This system deals with events coming and going from
a particular class. Classes can send events and a
particular action can be taken on an events
"""

class Observer: # pylint: disable=no-init
	"""
	Event Observer

	Listen for events, that can or should be acted on in a specific way. Event
	listeners are associated with callables that are called based on what the
	event called was.
	"""
	__events = {}
	__send = {}
	__also = []

	def add_listener(self, name, callback):
		"""
		Send some data to an event handler so that some work may be done when an
		event happens
		"""
		name = name.lower()
		if not name in self.__events:
			self.__events[name] = []
		self.__events[name].append(callback)

	def remove_listeners(self, name):
		""" Remove all the listeners that are associated with a particular name """
		if name in self.__events:
			del self.__events[name]

	def on(self, name, callback): # pylint: disable=invalid-name
		""" Alias for add_listener """
		self.add_listener(name, callback)

	def off(self, name):
		""" Alias for remove_listeners """
		self.remove_listeners(name)

	def send(self, name, data=None):
		"""
		Send the event named `name` with the data `data` so that the callbacks may
		be called with each of the data as arguments
		"""
		name = name.lower()
		if name in self.__events:
			for event_callable in self.__events[name]:
				if isinstance(data, list) or isinstance(data, tuple):
					data = list(data)
				else:
					data = [data]
				data.extend(self.__also)
				event_callable(self, *data) # pylint: disable=star-args
		else:
			if name not in self.__send:
				self.__send[name] = []
			self.__send[name].append(data)

	def also(self, *args):
		"""
		We may want to pass a specific pre-determined message with each
		event that we fire (a configuration object, for example). The
		Observer.also() command allows us to specify this before hand. Messages
		passed into the Observer with also() will be exended onto the end of the
		argument list.
		"""
		if not isinstance(args, list):
			args = list(args)
		self.__also.extend(args)
