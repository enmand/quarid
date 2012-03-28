"""
Event management system

This system deals with events coming and going from
a particular class. Classes can send events and a 
particular action can be taken on an events
"""

class Observer:
	__events 	= {};
	__send 		= {};
	__also		= [];

	"""
	Send some data to an event handler so that
	some work may be done when an event happens
	"""
	def addListener(self, name, callback):
		name = name.lower();
		if not name in self.__events:
			self.__events[name] = [];
		self.__events[name].append(callback);

	"""
	Remove all the listeners that are associated
	with a particular name
	"""
	def removeListeners(name):
		if name in __events:
			del self.__events[name];

	"""
	Alias for addListener
	"""
	def on(self, name, callback):
		self.addListener(name, callback);

	"""
	Alias for removeListeners
	"""
	def off(self, name):
		self.removeListeners(name);

	"""
	Send the event named `name` with the data `data`
	so that the callbacks may be called with each of
	the data as arguments
	"""
	def send(self, name, data = None):
		name = name.lower();
		if name in self.__events:
			for ev in self.__events[name]:
				if isinstance(data, list) or isinstance(data, tuple):
					data = list(data);
				else:
					data = [data];
				data.extend(self.__also);
				ev(self, *data);
		else:
			if name not in self.__send:
				self.__send[name] = [];
			self.__send[name].append(data);

	"""
	We may want to pass a specific pre-determined message with each
	event that we fire (a configuration object, for example). The
	Observer.also() command allows us to specify this before hand. Messages
	passed into the Observer with also() will be exended onto the end of the
	argument list.
	"""
	def also(self, *args):
		if not isinstance(args, list):
			args = list(args);
		self.__also.extend(args);
