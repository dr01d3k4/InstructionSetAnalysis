from __future__ import print_function;
from util.byte_util import getDisplayByteString;


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
	"jump unsigned",
	"jump signed"
];


def opcodeTypeToString(opcodeType):
	if ((opcodeType < 0) or (opcodeType >= len(OPCODE_TYPES))):
		return "None";
	else:
		return OPCODE_TYPES[opcodeType];



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


def getOpcodeParam(opcodeDetails, parameter):
	if (parameter in opcodeDetails):
		return opcodeDetails[parameter];
	else:
		if (parameter in opcodeParameterDefaults):
			return opcodeParameterDefaults[parameter];
		else:
			print("Unknown opcode parameter:", str(parameter));
			return None;


# def toString(opcode, extension = -1):
# 	# -1 indicates no extension
# 	if ((extension < -1) or (extension > 7)):
# 		print("Opcode extension out of bounds");

# 	if (opcode == 0x00):
# 		return "";
# 	elif ((opcode == 0x89) or (opcode == 0x8b) or (opcode == 0xb8)):
# 		return "mov";
# 	elif (opcode == 0xc7):
# 		return "mov";
# 	elif (opcode == 0x63):
# 		return "movsxd";
# 	elif (opcode == 0x83):
# 		extensions = ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"];
# 		return extensions[extension];
# 	elif (opcode == 0x01):
# 		return "add";
# 	elif (opcode == 0x50):
# 		return "push";
# 	elif (opcode == 0x58):
# 		return "pop";
# 	elif (opcode == 0xe8):
# 		return "call";
# 	elif (opcode == 0xc3):
# 		return "ret";
# 	elif (opcode == 0xc9):
# 		return "leave";
# 	elif (opcode == 0x98):
# 		return "cdqe";


# 	elif (opcode == 0xc1):
# 		extensions = ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"];
# 		return extensions[extension];
# 	elif (opcode == 0x8d):
# 		return "lea";
# 	elif (opcode == 0xf7):
# 		extensions = ["test", "test", "not", "neg", "mul", "imul", "div", "idiv"];
# 		return extensions[extension];
# 	elif (opcode == 0x6b):
# 		return "imul";
# 	elif (opcode == 0x29):
# 		return "sub";
# 	elif (opcode == 0xeb):
# 		return "jmp";
# 	elif (opcode == 0x3b):
# 		return "cmp";
# 	elif (opcode == 0x7c):
# 		return "jl";

# 	elif (opcode == 0x0faf):
# 		return "imul";

# 	else:
# 		print("Unknown opcode: " + getDisplayByteString(opcode));
# 		return "";