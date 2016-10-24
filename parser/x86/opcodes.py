from __future__ import print_function;
from util.byte_util import getDisplayByteString;


"""
Fields available:

Field name			Default value		Effect
- dataSize			[ do nothing ]		Call rexPrefix.setDataSize()
- readModRegRm			False
- rmIsSource			True
- opcodeExtension		False
- readImmediateBytes		0

"""


opcodeParameterDefaults = {
	"dataSize": 64,
	"readModRegRm": False,
	"rmIsSource": True,
	"opcodeExtension": False,
	"readImmediateBytes": 0	
};


top5BitsOpcodes = {
	# push
	0x50: {
		"dataSize": 64
	},

	# pop
	0x58: {
		"dataSize": 64
	},

	# mov imm32 -> r32
	0xb8: {
		"dataSize": 32,
		"readImmediateBytes": 4
	}
};

oneByteOpcodes = {
	# nop
	0x00: { },

	# add r to rm
	0x01: {
		"readModRegRm": True,
		"rmIsSource": False
	},

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm8 to r/m16/32
	0x83: {
		"opcodeExtension": True,
		"readModRegRm": True,
		"rmIsSource": False,
		"readImmediateBytes": 1
	},

	# mov r/m -> r
	0x89: {
		"rmIsSource": False,
		"readModRegRm": True
	},

	# mov r -> r/m
	0x8b: {
		"readModRegRm": True
	},

	# move imm32 -> rm32
	0xc7: {
		"readModRegRm": True,
		"opcodeExtension": True,
		"rmIsSource": False
	},

	# movsxd r64 -> r/m32 with rex.w
	0x63: {
		"readModRegRm": True,
		"rmIsSource": False
	},

	# call near rel16/32
	0xe8: {
		"readImmediateBytes": 4
	},

	# jmp rel8
	0xeb: {
		"readImmediateBytes": 1
	},

	# jmp rel8
	0x7c: {
		"readImmediateBytes": 1
	},

	# return near
	0xc3: { },

	# leaveq
	0xc9: { },

	# cltq
	0x98: { },

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift r/m by imm
	0xc1: {
		"readModRegRm": True,
		"opcodeExtension": True,
		"rmIsSource": False,
		"readImmediateBytes": 1
	},

	# lea
	0x8d: {
		"readModRegRm": True,
	},

	# test/test/not/neg/mul/imul/div/idiv
	0xf7: {
		"opcodeExtension": True,
		"readModRegRm": True
	},

	# imul
	0x6b: {
		"readModRegRm": True,
		"rmIsSource": True,
		"readImmediateBytes": 1
	},

	# sub
	0x29: {
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cmp
	0x3b: {
		"readModRegRm": True
	}
};


twoByteOpcodes = {
	# imul
	0xaf: {
		"readModRegRm": True,
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
		return "movl";
	elif (opcode == 0x63):
		return "movslq";
	elif (opcode == 0x83):
		extensions = ["addl", "or", "adc", "sbb", "and", "sub", "xor", "cmp"];
		return extensions[extension];
	elif (opcode == 0x01):
		return "add";
	elif (opcode == 0x50):
		return "push";
	elif (opcode == 0x58):
		return "pop";
	elif (opcode == 0xe8):
		return "callq";
	elif (opcode == 0xc3):
		return "retq";
	elif (opcode == 0xc9):
		return "leaveq";
	elif (opcode == 0x98):
		return "cltq";


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