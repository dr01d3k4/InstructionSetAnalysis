import array;
import endian;


"""
Turns a hexadecimal number in a string to an integer.
"""
def hexStringToInteger(string):
	return int(string.encode("hex"), 16);


def getDisplayByteString(byte):
	return "Dec: " + str(byte) + "; \tHex: " + byteToHexString(byte) + "; \tBin: " + byteToBinaryString(byte);


"""
Read n bytes from file f (advancing the file pointer).
Returns an array of integers where each integer is a byte from the file.
Also returns the raw data from the file.
"""
# def readBytes(f, n):
# 	s = f.read(n);
# 	bytes = array.array("B", map(hexStringToInteger, s));

# 	return bytes;


def readBytes(f, dataSize, endianness = endian.BIG, dataCount = 1):
	s = f.read(dataSize * dataCount);

	bytes = map(hexStringToInteger, s)

	# If little endian and dealing with a type larger than 1 byte big
	if ((endianness == endian.LITTLE) and (dataSize > 1)):
		if (dataCount > 1):
			# If array then flip individual elements
			newBytes = [ ];
			for i in xrange(0, dataSize * dataCount, dataSize):
				originalBytes = bytes[i:(i + dataSize)];
				originalBytes.reverse();
				newBytes += originalBytes;
			bytes = newBytes;
		else:
			# 1 single value, not array, so can flip whole type
			bytes.reverse();

	return array.array("B", bytes);



"""
Takes an array of integers representing bytes
Returns array of strings of hex of the integers
"""
def bytesToHexArray(bytes):
	return str(map(hex, bytes));


"""
Returns a byte represented as hexadecimal string.
Prefix bool adds 0x to the start.
Length is how long to pad the byte with 0s
"""
def byteToHexString(i, prefix = False, length = 2):
	s = ("0x" if prefix else "") + "%0." + str(length) + "x";
	return s % i;


def byteToHexStringSpaceAlign(i, prefix = False, length = 2):
	s = str(hex(i))[2:];
	while (len(s) < length):
		s = " " + s;
	if (prefix):
		s = "0x" + s;
	return s;
 


def byteToBinaryString(i, prefix = False, length = 8):
	s = str(bin(i))[2:];
	while (len(s) < length):
		s = "0" + s;
	if (prefix):
		s = "0b" + s;
	return s;


"""
Takes an array of integers representing bytes
Returns a string of hexadecimal
E.g. [127, 69, 76, 70, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	-> 7f45 4c46 0201 0100 0000 0000 0000 0000
Bytes between spaces is how often to add a space, or 0 for no spaces.
Secondary space is the same for a second space (e.g. "ff ff  ff ff  ff ff  ff ff").
"""
def bytesToHexString(bytes, bytesBetweenSpaces = 2, secondarySpace = 0):
	if (bytes == None):
		return "None";

	s = "";
	i = 0;
	j = 0;

	for byte in bytes:
		s += byteToHexString(byte);

		if (bytesBetweenSpaces > 0):
			i += 1;
			if (i >= bytesBetweenSpaces):
				s += " ";
				i = 0;

		if (secondarySpace > 0):
			j += 1;
			if (j >= secondarySpace):
				s += " ";
				j = 0;


	while ((len(s) > 0) and (s[-1] == " ")):
		s = s[:-1];

	return s;


"""
Turns an array of integers representing bytes into 1 integer
"""
def collapseBytesToInteger(bytes):
	n = 0;
	for i in bytes:
		n = (n << 8) + i;
	return n;


"""
Calls chr() on a byte if it's viewable, else return a dot.
"""
def byteToAsciiChar(byte):
	if ((byte >= 32) and (byte < 127)):
		return chr(byte);
	else:
		return ".";


"""
Turns array of integers representing bytes into array of chars.
Uses byteToAsciiChar()
"""
def bytesToAsciiCharString(bytes):
	return "".join(map(byteToAsciiChar, bytes));


"""
Reads a null terminated string starting at offset in bytes. Treats EOF as end of string.
"""
def readNullTerminatedString(bytes, offset):
	s = "";
	i = offset;
	while ((i < len(bytes)) and (bytes[i] != 0)):
		s += byteToAsciiChar(bytes[i]);
		i += 1;
	return s;
