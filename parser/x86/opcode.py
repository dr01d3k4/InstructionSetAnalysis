import opcodes;


class Opcode(object):
	def __init__(self, opcode, extension = -1):
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
		s = "Opcode(opcode = " + str(self._opcode);
		if (self._extension != -1):
			s += ", extension = " + str(self._extension);
		s += ", name = " + self._name;
		s += ")";
		return s;