from architecture.architecture_base import ArchitectureBase;
import decoder;
import opcode;
import operand;
import instruction;


class x86(ArchitectureBase):
	def __init__(self):
		super(ArchitectureBase, self).__init__();


	def decode(self, bytes, startDebugAt = -1):
		return decoder.decode(bytes, startDebugAt);


	def getName(self):
		return "x86";


	def getOpcodeTypes(self):
		return opcode.OPCODE_TYPES;


	def getCountOfUniqueOpcodesForTypes(self):
		print("TODO: Count opcodes for x86");
		return opcode.UNIQUE_OPCODE_TYPE_COUNT;


	def getUniqueOpcodeCount(self):
		print("TODO: Count opcodes for x86");
		return opcode.UNIQUE_OPCODE_COUNT;


	def getOperandTypes(self):
		return operand.OPERAND_TYPES;


	def getDataDirections(self):
		return instruction.DATA_DIRECTIONS;