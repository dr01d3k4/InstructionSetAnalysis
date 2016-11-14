from architecture.architecture_base import ArchitectureBase;
import decoder;
import opcode;
import operand;


class x86(ArchitectureBase):
	def __init__(self):
		super(ArchitectureBase, self).__init__();


	def decode(self, bytes, startDebugAt = -1):
		return decoder.decode(bytes, startDebugAt);


	def getName(self):
		return "x86";


	def getOpcodeTypes(self):
		return opcode.OPCODE_TYPES;


	def getOperandTypes(self):
		return operand.OPERAND_TYPES;