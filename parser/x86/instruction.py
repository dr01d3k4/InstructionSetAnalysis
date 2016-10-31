from common.instruction_base import InstructionBase;


class Instruction(InstructionBase):
	def __init__(self, opcode, operands):
		super(InstructionBase, self).__init__();
		self._opcode = opcode;
		self._operands = operands;


	# @property
	def getOpcode(self):
		return self._opcode;


	# @property
	def getOperands(self):
		return self._operands;


	def getOpcodeType(self):
		return self._opcode.opcodeType;


	def __repr__(self):
		return "Instruction()";


	def toString(self, maxOpcodeLength = 0):
		s = self._opcode.name;

		if (len(self._operands) > 0):
			while (len(s) < maxOpcodeLength):
				s += " ";
			s += "  ";

			for operand in self._operands:
				s += str(operand);
				s += ", ";
			
			s = s[:-2];

		return s;


	def __str__(self):
		return self.toString(0);


	def __repr__(self):
		s = "Instruction(\n";
		s += "\topcode = " + repr(self._opcode) + "\n";
		s += "\toperands = [";
		if (len(self._operands) > 0):
			for operand in self._operands:
				s += "\n\t\t" + repr(operand);
				s += ",";
			s = s[:-1];
			s += "\n\t";
		s += "]\n";
		s += ")";

		return s;