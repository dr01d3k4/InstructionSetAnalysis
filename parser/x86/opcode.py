from __future__ import print_function;
from util.byte_util import getDisplayByteString;


TRANSFER_TYPE = 0;
ARITHMETIC_TYPE = 1;
LOGIC_TYPE = 2;
MISC_TYPE = 3;
JUMP_TYPE = 4;
JUMP_UNSIGNED_TYPE = 5;
JUMP_SIGNED_TYPE = 6;


OPCODE_TYPES = [
	"transfer",
	"arithmetic",
	"logic",
	"misc",
	"jump",
	# "jump unsigned",
	# "jump signed"
];


def opcodeTypeToString(opcodeType):
	if ((opcodeType < 0) or (opcodeType >= len(OPCODE_TYPES))):
		return "None";
	else:
		return OPCODE_TYPES[opcodeType];


"""
Fields available:

Field name			Default value		Effect
- name				
- opcodeType
- dataSize			[ do nothing ]		Call rexPrefix.setDataSize()
- opcodeExtension		False
- readModRegRm			False
- rmIsSource			True
- readImmediateBytes		0
"""


opcodeParameterDefaults = {
	"dataSize": 64,
	"opcodeExtension": False,
	"readModRegRm": False,
	"rmIsSource": True,
	"readImmediateBytes": 0
};


top5BitsOpcodes = {
	# push
	0x50: {
		"name": "push",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 64
	},

	# pop
	0x58: {
		"name": "pop",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 64

	},

	# mov imm32 -> r32
	0xb8: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 32,
		"readImmediateBytes": 4
	}
};

oneByteOpcodes = {
	# nop
	0x00: {
		"name": "nop",
		"opcodeType": MISC_TYPE
	},

	# add r to rm
	0x01: {
		"name": "add",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm8 to r/m16/32
	0x83: {
		"name": ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# mov r/m -> r
	0x89: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True
	},

	# mov r -> r/m
	0x8b: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# mov imm32 -> rm32
	0xc7: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True
	},

	# movsxd r64 -> r/m32 with rex.w
	0x63: {
		"name": "movsxd",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True
	},

	# call near rel16/32
	0xe8: {
		"name": "call",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 4
	},

	# jmp rel8
	0xeb: {
		"name": "jmp",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 1
	},

	# jmp rel8
	0x7c: {
		"name": "jl",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 1
	},

	# return near
	0xc3: {
		"name": "ret",
		"opcodeType": JUMP_TYPE
	},

	# leave
	0xc9: {
		"name": "leave",
		"opcodeType": JUMP_TYPE
	},

	# cdqe
	0x98: {
		"name": "cdqe",
		"opcodeType": TRANSFER_TYPE
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift r/m by imm
	0xc1: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# lea
	0x8d: {
		"name": "lea",
		"opcodeType": MISC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# test/test/not/neg/mul/imul/div/idiv
	0xf7: {
		"name": ["test", "test", "not", "neg", "mul", "imul", "div", "idiv"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True
	},

	# imul
	0x6b: {
		"name": "imul",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# sub
	0x29: {
		"name": "sub",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# cmp
	0x3b: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	}
};


twoByteOpcodes = {
	# imul
	0xaf: {
		"name": "imul",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	}
};


def getOpcodeParamOrDefault(opcodeDetails, parameter):
	if (parameter in opcodeDetails):
		return opcodeDetails[parameter];
	else:
		if (parameter in opcodeParameterDefaults):
			return opcodeParameterDefaults[parameter];
		else:
			print("Unknown opcode parameter:", str(parameter));
			return None;


class Opcode(object):
	def __init__(self, opcode, extension, name, opcodeType):
		self._opcode = opcode;
		self._extension = extension;
		self._name = name;
		self._opcodeType = opcodeType;


	@property
	def opcode(self):
		return self._opcode;


	@property
	def extension(self):
		return self._extension;


	@property
	def name(self):
		return self._name;


	@property
	def opcodeType(self):
		return self._opcodeType;


	def __repr__(self):
		s = "Opcode(opcode = " + hex(self._opcode);
		if (self._extension != -1):
			s += ", extension = " + hex(self._extension);
		s += ", name = " + self._name;
		s += ", type = " + opcodeTypeToString(self._opcodeType);
		s += ")";
		return s;