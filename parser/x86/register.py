# Registers
# https://en.wikibooks.org/wiki/X86_Assembly/X86_Architecture#General-Purpose_Registers_.28GPR.29_-_16-bit_naming_conventions
"""
000 = EAX (AX if data size is 16 bits, AL if 8)
001 = ECX/CX/CL
010 = EDX/DX/DL
011 = EBX/BX/BL
100 = ESP/SP (AH if data size is 8 bits)
101 = EBP/BP (CH if 8)
110 = ESI/SI (DH if 8)
111 = EDI/DI (BH if 8)
"""

class Register(object):
	def __init__(self, name, bitRepresentation):
		self._name = name;
		self._bitRepresentation = bitRepresentation;

	def __repr__(self):
		return "Register(" + \
			self._name + ", " + \
			self._bitRepresentation + \
			")";

	def __str__(self):
		return self._name.lower();


Registers = [
	[
		Register("AL", "000"),
		Register("CL", "001"),
		Register("DL", "010"),
		Register("BL", "011"),
		Register("AH", "100"),
		Register("CH", "101"),
		Register("DH", "110"),
		Register("BH", "111")
	],
	[
		Register("AX", "000"),
		Register("CX", "001"),
		Register("DX", "010"),
		Register("BX", "011"),
		Register("SP", "100"),
		Register("BP", "101"),
		Register("SI", "110"),
		Register("DI", "111")
	],
	[
		Register("EAX", "000"),
		Register("ECX", "001"),
		Register("EDX", "010"),
		Register("EBX", "011"),
		Register("ESP", "100"),
		Register("EBP", "101"),
		Register("ESI", "110"),
		Register("EDI", "111")
	],
	[
		Register("RAX", "000"),
		Register("RCX", "001"),
		Register("RDX", "010"),
		Register("RBX", "011"),
		Register("RSP", "100"),
		Register("RBP", "101"),
		Register("RSI", "110"),
		Register("RDI", "111")
	],
	[
		Register("R8",  "000"),
		Register("R9",  "001"),
		Register("R10", "010"),
		Register("R11", "011"),
		Register("R12", "100"),
		Register("R13", "101"),
		Register("R14", "110"),
		Register("R15", "111")
	]
];


def getRegister(registerId, rexPrefix, adjustingBit = False):
	if ((registerId < 0) or (registerId >= 8)):
		print("Invalid register:", registerId);
		return None;

	dataSize = rexPrefix.getDataSize();

	if ((dataSize != 8) and (dataSize != 16) and (dataSize != 32) and (dataSize != 64)):
		print("Invalid data size:", dataSize);
		return None;

	adjustedSize = 0;
	if (dataSize == 16):
		adjustedSize = 1;
	elif (dataSize == 32):
		adjustedSize = 2;
	elif (dataSize == 64):
		adjustedSize = 3;

	if (registerId == 4) or (registerId == 5):
		adjustedSize = 3;

	if (adjustingBit):
		return Registers[4][registerId];
	else:
		return Registers[adjustedSize][registerId];


def getRegRegister(registerId, rexPrefix):
	return getRegister(registerId, rexPrefix, rexPrefix.getR());


def getRmRegister(registerId, rexPrefix):
	return getRegister(registerId, rexPrefix, rexPrefix.getB());


def getBaseRegister(registerId, rexPrefix):
	return getRegister(registerId, rexPrefix, rexPrefix.getB());


def getIndexRegister(registerId, rexPrefix):
	return getRegister(registerId, rexPrefix, rexPrefix.getX());