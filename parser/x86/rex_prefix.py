import abc;


class RexPrefixBase(object):
	__metaclass__ = abc.ABCMeta;

	@abc.abstractmethod
	def getDataSize(self):
		return;

	@abc.abstractmethod
	def setDataSize(self, dataSize):
		return;

	@abc.abstractmethod
	def getB(self):
		return;



class RexPrefix(RexPrefixBase):
	def __init__(self, w, r, x, b):
		self._w = w;
		self._r = r;
		self._x = x;
		self._b = b;

	def set(self, w, r, x, b):
		self._w = w;
		self._r = r;
		self._x = x;
		self._b = b;

	@property
	def w(self):
		return self._w;

	@property
	def r(self):
		return self._r;

	@property
	def x(self):
		return self._x;

	@property
	def b(self):
		return self._b;

	def getDataSize(self):
		size = 64 if self._w else 32;
		return size;

	def setDataSize(self, dataSize):
		self._w = (dataSize == 64);

	def getB(self):
		return True if self._b else False;

	def __repr__(self):
		return "RexPrefix(" + \
			"w = " + str(self._w) + ", " + \
			"r = " + str(self._r) + ", " + \
			"x = " + str(self._x) + ", " + \
			"b = " + str(self._b) + \
			")";

	def __str__(self):
		return self.__repr__();


class NoRexPrefix(RexPrefixBase):
	def __init__(self, dataSize = 32):
		self._dataSize = dataSize;

	def getDataSize(self):
		return self._dataSize;

	def setDataSize(self, dataSize):
		self._dataSize = dataSize;

	def getB(self):
		return False;

	def __repr__(self):
		return "NoRexPrefix(dataSize = " + str(self._dataSize) + ")";

	def __str__(self):
		return self.__repr__();