import abc;


class RexPrefixBase(object):
	__metaclass__ = abc.ABCMeta;

	@abc.abstractmethod
	def getDataSize(self):
		pass;

	@abc.abstractmethod
	def withDataSize(self, dataSize):
		pass;

	@abc.abstractmethod
	def getW(self):
		pass;

	@abc.abstractmethod
	def getR(self):
		pass;

	@abc.abstractmethod
	def getX(self):
		pass;

	@abc.abstractmethod
	def getB(self):
		pass;


class RexPrefix(RexPrefixBase):
	def __init__(self, w, r, x, b):
		super(RexPrefixBase, self).__init__();
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

	def withDataSize(self, dataSize):
		return RexPrefix(dataSize == 64, self._r, self._x, self._b);
		# return getRexPrefix(dataSize == 64, self._r, self._x, self._b);

	def getW(self):
		return True if self._w else False;

	def getR(self):
		return True if self._r else False;

	def getX(self):
		return True if self._x else False;

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
		super(RexPrefixBase, self).__init__();
		self._dataSize = dataSize;

	def getDataSize(self):
		return self._dataSize;

	def withDataSize(self, dataSize):
		# self._dataSize = dataSize;
		return NoRexPrefix(dataSize);
		# return getNoRexPrefix(dataSize);

	def getW(self):
		return False;

	def getR(self):
		return False;

	def getX(self):
		return False;

	def getB(self):
		return False;

	def __repr__(self):
		return "NoRexPrefix(dataSize = " + str(self._dataSize) + ")";

	def __str__(self):
		return self.__repr__();


RexPrefixes = [
	RexPrefix(False, False, False, False),
	RexPrefix(False, False, False, True),
	RexPrefix(False, False, True, False),
	RexPrefix(False, False, True, True),
	RexPrefix(False, True, False, False),
	RexPrefix(False, True, False, True),
	RexPrefix(False, True, True, False),
	RexPrefix(False, True, True, True),
	RexPrefix(True, False, False, False),
	RexPrefix(True, False, False, True),
	RexPrefix(True, False, True, False),
	RexPrefix(True, False, True, True),
	RexPrefix(True, True, False, False),
	RexPrefix(True, True, False, True),
	RexPrefix(True, True, True, False),
	RexPrefix(True, True, True, True),
];

NoRexPrefix8 = NoRexPrefix(8);
NoRexPrefix16 = NoRexPrefix(16);
NoRexPrefix32 = NoRexPrefix(32);
NoRexPrefix64 = NoRexPrefix(64);


def getRexPrefix(w, r, x, b):
	number = 0;
	if (w):
		number = number | 0x08;
	if (r):
		number = number | 0x04;
	if (x):
		number = number | 0x02;
	if (b):
		number = number | 0x01;

	return getRexPrefixFromNumber;


def getRexPrefixFromNumber(number):
	if ((number < 0) or (number >= len(RexPrefixes))):
		print("Unknown rex number");
		return None;
	else:
		return RexPrefixes[number];


def getNoRexPrefix(dataSize = 32):
	if (dataSize == 8):
		return NoRexPrefix8;
	elif (dataSize == 16):
		return NoRexPrefix16;
	elif (dataSize == 32):
		return NoRexPrefix32;
	elif (dataSize == 64):
		return NoRexPrefix64;
	else:
		print("Unknown data size for no rex prefix");
		return None;