from compiler_base import CompilerBase;


class gcc(CompilerBase):
	def __init__(self):
		super(CompilerBase, self).__init__();


	def getName(self):
		return "gcc";