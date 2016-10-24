from abc import ABCMeta;


def immediateValueToString(value):
	return "$" + hex(value);


def registerValueToString(register):
	return "%" + str(register);


def scaleIndexBaseToString(scale, index, base):
	sib = "(";
	if (base != None):
		sib += registerValueToString(base);
	sib += ", ";
	if (index != None):
		sib += registerValueToString(index);
	sib += ", ";
	sib += str(scale);
	sib += ")";
	return sib;



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
		return "ImmediateOperand(value = " + repr(self._value) + ")";

	def __str__(self):
		return immediateValueToString(self._value);


class RegisterDisplacementOperand(Operand):
	def __init__(self, register, displacement):
		super(Operand, self).__init__();

		self._register = register;
		self._displacement = displacement;

	def __repr__(self):
		return "RegisterDisplacementOperand(register = " + repr(self._register) + ", displacement = " + repr(self._displacement) + ")";

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
		return scaleIndexBaseToString(self._scale, self._index, self._base);


class ScaleIndexBaseDisplacementOperand(Operand):
	def __init__(self, scale, index, base, displacement):
		super(Operand, self).__init__();

		self._scale = scale;
		self._index = index;
		self._base = base;
		self._displacement = displacement;

	def __repr__(self):
		return "ScaleIndexBaseDisplacementOperand(" \
				"scale = " + str(self._scale) + ", " + \
				"index = " + repr(self._index) + ", " + \
				"base = " + repr(self._base) + ", " + \
				"displacement = " + repr(self._displacement) + ")";

	def __str__(self):
		return immediateValueToString(self._displacement)[1:] + scaleIndexBaseToString(self._scale, self._index, self._base);


class ImmediateDisplacementOperand(Operand):
	def __init__(self, value):
		super(Operand, self).__init__();

		self._value = value;

	def __repr__(self):
		return "ImmediateDisplacementOperand(value = " + repr(self._value) + ")";

	def __str__(self):
		return "(" + immediateValueToString(self._value) + ")";
