from __future__ import print_function;
from util.byte_util import getDisplayByteString;


"""
Fields available:

Field name			Default value		Effect
- dataSize			[ do nothing ]		Call rexPrefix.setDataSize()
- readModRegRm			False
# - rmIsSource			True
- opcodeExtension		False
- readImmediateBytes		0
- opcodeType			UNKNOWN_TYPE
"""

TRANSFER_TYPE = 0;
ARITHMETIC_TYPE = 1;
LOGIC_TYPE = 2;
MISC_TYPE = 3;
JUMP_TYPE = 4;
JUMP_UNSIGNED_TYPE = 5;
JUMP_SIGNED_TYPE = 6;
UNKNOWN_TYPE = 7;


OPCODE_TYPES = [
	"transfer",
	"arithmetic",
	"logic",
	"misc",
	"jump",
	"jump unsigned",
	"jump signed",
	"unknown type"
];


def opcodeTypeToString(opcodeType):
	if ((opcodeType < 0) or (opcodeType >= len(OPCODE_TYPES))):
		return "None";
	else:
		return OPCODE_TYPES[opcodeType];



opcodeParameterDefaults = {
	"dataSize": 64,
	"readModRegRm": False,
	"rmIsSource": True,
	"opcodeExtension": False,
	"readImmediateBytes": 0,
	"opcodeType": UNKNOWN_TYPE
};


top5BitsOpcodes = {
	# push
	0x50: {
		"dataSize": 64,
		"opcodeType": TRANSFER_TYPE
	},

	# pop
	0x58: {
		"dataSize": 64,
		"opcodeType": TRANSFER_TYPE

	},

	# mov imm32 -> r32
	0xb8: {
		"dataSize": 32,
		"readImmediateBytes": 4,
		"opcodeType": TRANSFER_TYPE
	}
};

oneByteOpcodes = {
	# nop
	0x00: {
		"opcodeType": MISC_TYPE
	},

	# add r to rm
	0x01: {
		"readModRegRm": True,
		"opcodeType": ARITHMETIC_TYPE
	},

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm8 to r/m16/32
	0x83: {
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1,
		"opcodeType": ARITHMETIC_TYPE
	},

	# mov r/m -> r
	0x89: {
		"readModRegRm": True,
		"opcodeType": TRANSFER_TYPE
	},

	# mov r -> r/m
	0x8b: {
		"rmIsSource": False,
		"readModRegRm": True,
		"opcodeType": TRANSFER_TYPE
	},

	# mov imm32 -> rm32
	0xc7: {
		"readModRegRm": True,
		"opcodeExtension": True,
		"opcodeType": TRANSFER_TYPE
	},

	# movsxd r64 -> r/m32 with rex.w
	0x63: {
		"readModRegRm": True,
		"opcodeType": TRANSFER_TYPE
	},

	# call near rel16/32
	0xe8: {
		"readImmediateBytes": 4,
		"opcodeType": JUMP_TYPE
	},

	# jmp rel8
	0xeb: {
		"readImmediateBytes": 1,
		"opcodeType": JUMP_TYPE
	},

	# jmp rel8
	0x7c: {
		"readImmediateBytes": 1,
		"opcodeType": JUMP_TYPE
	},

	# return near
	0xc3: {
		"opcodeType": JUMP_TYPE
	},

	# leave
	0xc9: {
		"opcodeType": JUMP_TYPE
	},

	# cdqe
	0x98: {
		"opcodeType": TRANSFER_TYPE
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift r/m by imm
	0xc1: {
		"readModRegRm": True,
		"opcodeExtension": True,
		"readImmediateBytes": 1,
		"opcodeType": ARITHMETIC_TYPE
	},

	# lea
	0x8d: {
		"readModRegRm": True,
		"rmIsSource": False,
		"opcodeType": MISC_TYPE
	},

	# test/test/not/neg/mul/imul/div/idiv
	0xf7: {
		"opcodeExtension": True,
		"readModRegRm": True,
		"opcodeType": ARITHMETIC_TYPE
	},

	# imul
	0x6b: {
		"readModRegRm": True,
		"readImmediateBytes": 1,
		"opcodeType": ARITHMETIC_TYPE
	},

	# sub
	0x29: {
		"readModRegRm": True,
		"opcodeType": ARITHMETIC_TYPE
	},

	# cmp
	0x3b: {
		"readModRegRm": True,
		"rmIsSource": False,
		"opcodeType": ARITHMETIC_TYPE
	}
};


twoByteOpcodes = {
	# imul
	0xaf: {
		"readModRegRm": True,
		"rmIsSource": False,
		"opcodeType": ARITHMETIC_TYPE
	}
};


def getOpcodeParam(opcodeDetails, parameter):
	if (parameter in opcodeDetails):
		return opcodeDetails[parameter];
	else:
		if (parameter in opcodeParameterDefaults):
			return opcodeParameterDefaults[parameter];
		else:
			print("Unknown opcode parameter:", str(parameter));
			return None;


def toString(opcode, extension = -1):
	# -1 indicates no extension
	if ((extension < -1) or (extension > 7)):
		print("Opcode extension out of bounds");

	if (opcode == 0x00):
		return "";
	elif ((opcode == 0x89) or (opcode == 0x8b) or (opcode == 0xb8)):
		return "mov";
	elif (opcode == 0xc7):
		return "mov";
	elif (opcode == 0x63):
		return "movsxd";
	elif (opcode == 0x83):
		extensions = ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"];
		return extensions[extension];
	elif (opcode == 0x01):
		return "add";
	elif (opcode == 0x50):
		return "push";
	elif (opcode == 0x58):
		return "pop";
	elif (opcode == 0xe8):
		return "call";
	elif (opcode == 0xc3):
		return "ret";
	elif (opcode == 0xc9):
		return "leave";
	elif (opcode == 0x98):
		return "cdqe";


	elif (opcode == 0xc1):
		extensions = ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"];
		return extensions[extension];
	elif (opcode == 0x8d):
		return "lea";
	elif (opcode == 0xf7):
		extensions = ["test", "test", "not", "neg", "mul", "imul", "div", "idiv"];
		return extensions[extension];
	elif (opcode == 0x6b):
		return "imul";
	elif (opcode == 0x29):
		return "sub";
	elif (opcode == 0xeb):
		return "jmp";
	elif (opcode == 0x3b):
		return "cmp";
	elif (opcode == 0x7c):
		return "jl";

	elif (opcode == 0x0faf):
		return "imul";

	else:
		print("Unknown opcode: " + getDisplayByteString(opcode));
		return "";