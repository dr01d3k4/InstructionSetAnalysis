import abc;


class CompilerBase(object):
	__metaclass__ = abc.ABCMeta;


	def __init__(self):
		pass;


	@abc.abstractmethod
	def getName(self):
		pass;