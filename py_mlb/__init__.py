from logging import getLogger, Handler

__version__ = '1.55'

class NullHandler(Handler):
	def emit(self, record):
		pass

def formatValue(val):
	"""
	Returns a properly casted variable for val
	"""
	if val.isdigit():
		val = int(val)
	else:
		try:
			val = float(val)
		except ValueError:
			val = val.encode('ascii', 'ignore')

	return val

def parseJSON(obj):
	"""
	Recursively parses a JSON object to properly cast ints and floats

	Arguments:
	obj : The JSON object
	"""
	newobj = {}

	for key, value in obj.iteritems():
		key = key.encode('ascii', 'ignore')

		if isinstance(value, dict):
			newobj[key] = parseJSON(value)
		elif isinstance(value, list):
			if key not in newobj:
				newobj[key] = []
				for i in value:
					newobj[key].append(parseJSON(i))
		elif isinstance(value, unicode):
			newobj[key] = formatValue(value)

	return newobj

logger = getLogger(__name__)
logger.addHandler(NullHandler())
