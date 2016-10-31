import abc;


class OpcodeBase(object):
	__metaclass__ = abc.ABCMeta;


	def __init__(self):
		pass;


	@abc.abstractmethod
	def getOpcodeType(self):
		pass;