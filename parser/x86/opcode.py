from common.opcode_base import OpcodeBase;
import opcodes;


class Opcode(OpcodeBase):
	def __init__(self, opcode, extension = -1, opcodeType = opcodes.UNKNOWN_TYPE):
		super(OpcodeBase, self).__init__();
		self._opcode = opcode;
		self._extension = extension;
		self._name = opcodes.toString(opcode, extension);
		self._opcodeType = opcodeType;

	@property
	def opcode(self):
		return self._opcode;

	@property
	def extension(self):
		return self._extension;

	@property
	def name(self):
		return self._name;

	@property
	def opcodeType(self):
		return self._opcodeType;

	def getOpcodeType(self):
		# return opcode_types.getOpcodeType(self);
		return self._opcodeType;

	def __repr__(self):
		s = "Opcode(opcode = " + hex(self._opcode);
		if (self._extension != -1):
			s += ", extension = " + hex(self._extension);
		s += ", name = " + self._name;
		s += ", type = " + opcodes.opcodeTypeToString(self._opcodeType);
		s += ")";
		return s;
