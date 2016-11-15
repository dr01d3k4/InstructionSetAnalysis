from __future__ import print_function;
from architecture.instruction_base import InstructionBase;
import operand;

NO_DIR = 0;
IMM_DIR = 1;
REG_DIR = 2;
MEM_DIR = 3;
IMM_TO_REG_DIR = 4;
IMM_TO_MEM_DIR = 5;
REG_TO_REG_DIR = 6;
REG_TO_MEM_DIR = 7;
MEM_TO_REG_DIR = 8;
MEM_TO_MEM_DIR = 9;


DATA_DIRECTIONS = [
	"no operands",
	"imm",
	"reg",
	"mem",
	"imm -> reg",
	"imm -> mem",
	"reg -> reg",
	"reg -> mem",
	"mem -> reg",
	"mem -> mem"
];


class Instruction(InstructionBase):
	def __init__(self, prefixBytes, opcode, operands):
		super(InstructionBase, self).__init__();
		self._prefixBytes = prefixBytes;
		self._opcode = opcode;
		self._operands = operands;


	def getOpcode(self):
		return self._opcode;


	def getOperands(self):
		return self._operands;


	def getOpcodeType(self):
		return self._opcode.opcodeType;


	def getOperandTypes(self):
		return map(lambda o: (o.getOperandType(), o), self._operands);


	def getDataDirection(self):
		operandCount = len(self._operands);
		operandUsages = map(lambda o: o.getImmRegMemUsage(), self._operands);

		# source = -1;
		# target = -1;
		direction = NO_DIR;

		if (operandCount == 1):
			source = operandUsages[0];

			if (source == operand.USES_IMM):
				direction = IMM_DIR;
			elif (source == operand.USES_REG):
				direction = REG_DIR;
			elif (source == operand.USES_MEM):
				direction = MEM_DIR;

		elif (operandCount >= 2):
			source = operandUsages[-1];
			target = operandUsages[-2];

			if (source == operand.USES_IMM):
				if (target == operand.USES_REG):
					direction = IMM_TO_REG_DIR;
				elif (target == operand.USES_MEM):
					direction = IMM_TO_MEM_DIR;

			elif (source == operand.USES_REG):
				if (target == operand.USES_REG):
					direction = REG_TO_REG_DIR;
				elif (target == operand.USES_MEM):
					direction = REG_TO_MEM_DIR;

			elif (source == operand.USES_MEM):
				if (target == operand.USES_REG):
					direction = MEM_TO_REG_DIR;
				elif (target == operand.USES_MEM):
					direction = MEM_TO_MEM_DIR;

		# if (operandCount >= 3):
		# 	pass;
			# print("Instruction has more than 3 or more operands");
			# print(self);

		# print(self, "\t\t", DATA_DIRECTIONS[direction]);

		return direction;


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
		if (self._prefixBytes != 0):
			s += "\tprefixBytes = " + hex(self._prefixBytes) + "\n";
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