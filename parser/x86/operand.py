from abc import ABCMeta;


def immediateValueToString(value):
	s = hex(value);
	if (s[0] != '-'):
		s = "$" + s;
	return s;


class Operand(object):
	__metaclass__ = ABCMeta;

	def __init__(self):
		pass;

	def __repr__(self):
		return "Operand()";

	def __str__(self):
		return "";


class RegisterOperand(Operand):
	def __init__(self, register):
		super(Operand, self).__init__();

		self._register = register;

	def __repr__(self):
		return "RegisterOperand(register = " + repr(self._register) + ")";

	def __str__(self):
		return "%" + str(self._register);


class ImmediateOperand(Operand):
	def __init__(self, value):
		super(Operand, self).__init__();

		self._value = value;

	def __repr__(self):
		return "ImediateOperand(value = " + repr(self._value) + ")";

	def __str__(self):
		return immediateValueToString(self._value);


class RegisterDisplacementOperand(Operand):
	def __init__(self, register, displacement):
		super(Operand, self).__init__();

		self._register = register;
		self._displacement = displacement;

	def __repr__(self):
		return "RegisterDisplacementOperand(register = " + repr(self._register) + ", displaceement = " + repr(self._displacement) + ")";

	def __str__(self):
		return immediateValueToString(self._displacement) + "(%" + str(self._register) + ")";
