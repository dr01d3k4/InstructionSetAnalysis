from common.opcode_base import OpcodeBase;
import opcodes;
import opcode_types;


class Opcode(OpcodeBase):
	def __init__(self, opcode, extension = -1):
		super(OpcodeBase, self).__init__();
		self._opcode = opcode;
		self._extension = extension;
		self._name = opcodes.toString(opcode, extension);

	@property
	def opcode(self):
		return self._opcode;

	@property
	def extension(self):
		return self._extension;

	@property
	def name(self):
		return self._name;

	def __repr__(self):
		s = "Opcode(opcode = " + hex(self._opcode);
		if (self._extension != -1):
			s += ", extension = " + hex(self._extension);
		s += ", name = " + self._name;
		s += ")";
		return s;


	def getType(self):
		return opcode_types.getOpcodeType(self);