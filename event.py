"""
Event management system

This system deals with events coming and going from
a particular class. Classes can send events and a 
particular action can be taken on an events
"""

class Observer:
	__events = {};
	__send = {};

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
				if isinstance(data, tuple):
					ev(self, *data);
				else:
					ev(self, data);
		else:
			if name not in self.__send:
				self.__send[name] = [];
			self.__send[name].append(data);
			

if __name__ == "__main__":
	def doSomething(event, text):
		print(text);

	def doSomethingElse(event, text):
		print(text.swapcase())

	event = Observer();

	event.on('something', doSomething);
	event.on('something', doSomethingElse);

	event.send('something', "Print me!");
	event.send('something', "Print me!");
