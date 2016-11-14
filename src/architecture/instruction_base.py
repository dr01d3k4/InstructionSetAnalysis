import abc;


class InstructionBase(object):
	__metaclass__ = abc.ABCMeta;


	def __init__(self):
		pass;


	@abc.abstractmethod
	def getOpcode(self):
		pass;


	@abc.abstractmethod
	def getOperands(self):
		pass;


	@abc.abstractmethod
	def getOpcodeType(self):
		pass;


	@abc.abstractmethod
	def getOperandTypes(self):
		pass;


	@abc.abstractmethod
	def getDataDirection(self):
		pass;