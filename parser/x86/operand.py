from abc import ABCMeta;


def immediateValueToString(value):
	s = hex(value);
	# if (s[0] != '-'):
	# 	s = "$" + s;
	s = "$" + s;
	return s;


def registerValueToString(register):
	return "%" + str(register);



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
		return registerValueToString(self._register);


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
		if (self._displacement == 0):
			return "(" + registerValueToString(self._register) + ")"
		else:
			return immediateValueToString(self._displacement)[1:] + "(" + registerValueToString(self._register) + ")";



class ScaleIndexBaseOperand(Operand):
	def __init__(self, scale, index, base):
		super(Operand, self).__init__();

		self._scale = scale;
		self._index = index;
		self._base = base;

	def __repr__(self):
		return "ScaleIndexBaseOperand(" \
				"scale = " + str(self._scale) + ", " + \
				"index = " + repr(self._index) + ", " + \
				"base = " + repr(self._base) + ")";

	def __str__(self):
		return "(" + registerValueToString(self._base) + ", " + registerValueToString(self._index) + ", " + str(self._scale) + ")";