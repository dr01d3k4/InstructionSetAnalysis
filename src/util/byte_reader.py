class ByteReader(object):
	def __init__(self, bytes):
		self._bytes = bytes;
		self._index = 0;
		self._currentlyRead = [ ];

	def readByte(self):
		if (self._index >= len(self._bytes)):
			return None, self._index;

		byte = self._bytes[self._index];
		self._currentlyRead.append(byte);
		oldIndex = self._index;
		self._index += 1;
		return byte, oldIndex;

	def __len__(self):
		return len(self._bytes);

	def resetCurrentlyRead(self):
		self._currentlyRead = [ ];

	@property
	def index(self):
		return self._index;

	@property
	def currentlyRead(self):
		return self._currentlyRead;

	def goBack(self):
		if (self._index > 0):
			self._index = self._index - 1;

		if (len(self._currentlyRead) > 0):
			self._currentlyRead = self._currentlyRead[:-1];

	def __repr__(self):
		return "ByteReader(\n\t" + \
			"bytes = " + bytesToHexString(self._bytes) + ", \n\t" + \
			"index = " + str(self._index) + ", \n\t" + \
			"currentlyRead = " + bytesToHexString(self._currentlyRead) + "\n" + \
			")";

	def __str__(self):
		return self.__repr__();