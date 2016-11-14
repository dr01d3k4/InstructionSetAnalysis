from byte_util import readBytes, byteToHexString, bytesToHexString, byteToAsciiChar, bytesToAsciiCharString;
import binary_type;
import endian;


class BinaryFile(object):
	def __init__(self, filename):
		self._filename = filename;


	@property
	def filename(self):
		return self._filename;


	def __enter__(self):
		class BinaryFileReader(object):
			def __init__(self, filename):
				self._file = open(filename);
				self._endianness = endian.BIG;


			def readArray(self, dataSize, dataCount):
				return readBytes(self._file, dataSize, self._endianness, dataCount);


			def readChar(self):
				return readBytes(self._file, binary_type.CHAR, self._endianness);


			def readCharArray(self, n):
				# return self.readArray(binary_type.CHAR, n);
				return readBytes(self._file, binary_type.CHAR, self._endianness, n);


			def readHalf(self):
				return readBytes(self._file, binary_type.HALF, self._endianness);


			def readWord(self):
				return readBytes(self._file, binary_type.WORD, self._endianness);


			def readSword(self):
				return readBytes(self._file, binary_type.SWORD, self._endianness);


			def readXword(self):
				return readBytes(self._file, binary_type.XWORD, self._endianness);


			def readSxword(self):
				return readBytes(self._file, binary_type.SXWORD, self._endianness);


			def readAddr(self):
				return readBytes(self._file, binary_type.ADDR, self._endianness);


			def readOff(self):
				return readBytes(self._file, binary_type.OFF, self._endianness);


			def seek(self, offset, from_what = 0):
				self._file.seek(offset, from_what);


			def tell(self):
				return self._file.tell();


			@property
			def endianness(self):
				return self._endianness;


			@endianness.setter
			def endianness(self, value):
				if ((value == endian.BIG) or (value == endian.LITTLE)):
					self._endianness = value;


			def cleanup(self):
				self._file.close();


		self.reader = BinaryFileReader(self._filename);
		return self.reader;


	def __exit__(self, exc_type, exc_value, traceback):
		self.reader.cleanup();


def printHexDump(filename, bytesPerRow = 16, byteNumberLength = 4, primarySpace = 1, secondarySpace = 4, hideDuplicateLines = True):
	byteNumber = 0;
	bytes = [ ];
	prevByteArray = [ ];
	s = "";

	with BinaryFile(filename) as f:
		f.endianness = endian.BIG;

		while (True):
			bytes = f.readCharArray(bytesPerRow);

			if (not bytes):
				break;

			if (hideDuplicateLines and (bytes == prevByteArray)):
				print("*");
				continue;

			prevByteArray = bytes;

			s += byteToHexString(byteNumber, False, byteNumberLength);
			s += "    ";
			s += bytesToHexString(bytes, primarySpace, secondarySpace);
			s += "    ";
			s += "|";
			s += bytesToAsciiCharString(bytes);
			s += "|";

			print(s);
			s = "";

			byteNumber += len(bytes);