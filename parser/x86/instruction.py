from util.byte_util import byteToHexStringSpaceAlign, bytesToHexString;


class Instruction(object):
	def __init__(self, startByte, bytes, opcode, operands):
		self._startByte = startByte;
		self._bytes = bytes;
		self._opcode = opcode;
		self._operands = operands;


	@property
	def startByte(self):
		return self._startByte;

	@property
	def bytes(self):
		return self._bytes;

	@property
	def opcode(self):
		return self._opcode;

	@property
	def operands(self):
		return self._operands;

	def __repr__(self):
		return "Instruction()";


	def toString(self, startByteLength, maxBytesPerInstruction, maxOpcodeLength):
		s = "";
		s += byteToHexStringSpaceAlign(self._startByte, length = startByteLength);
		s += ": ";

		bytesString = bytesToHexString(self._bytes, bytesBetweenSpaces = 1);
		# 3 because 2 hex chars for 1 byte + 1 space char
		while (len(bytesString) < maxBytesPerInstruction * 3):
			bytesString += " ";

		s += bytesString;
		s += " ";

		if (len(self._operands) > 0):
			opcode = self._opcode.name;
			while (len(opcode) < maxOpcodeLength):
				opcode += " ";
			s += opcode;
			s += "  ";

			for operand in self._operands:
				s += str(operand);
				s += ", ";
			
			s = s[:-2];
		else:
			s += self._opcode.name;

		return s;


	def __str__(self):
		return self.toString(8, 16, 0);