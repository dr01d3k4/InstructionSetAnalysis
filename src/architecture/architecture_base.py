import abc;


class ArchitectureBase(object):
	__metaclass__ = abc.ABCMeta;


	def __init__(self):
		pass;


	@abc.abstractmethod
	def decode(self, bytes, firstByteOffset):
		pass;


	@abc.abstractmethod
	def getName(self):
		pass;


	@abc.abstractmethod
	def getOpcodeTypes(self):
		pass;


	@abc.abstractmethod
	def getCountOfUniqueOpcodesForTypes(self):
		pass;


	@abc.abstractmethod
	def getUniqueOpcodeCount(self):
		pass;


	@abc.abstractmethod
	def getOperandTypes(self):
		pass;


	@abc.abstractmethod
	def getDataDirections(self):
		pass;