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
- autoInsertRegister		False			E.g. 3d cmp wants ax/eax/rax auto added
"""


opcodeParameterDefaults = {
	"dataSize": 64,
	"opcodeExtension": False,
	"readModRegRm": False,
	"rmIsSource": True,
	"readImmediateBytes": 0,
	"autoInsertRegister": False
};


def jumpDetails(name, immediateSize = 1):
	return {
		"name": name,
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": immediateSize
	};


top5BitsOpcodes = {
	# push r16/32/64
	0x50: {
		"name": "push",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 64
	},

	# pop r16/32/64
	0x58: {
		"name": "pop",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 64

	},

	# mov imm16/32/64 -> r16/32/64
	0xb8: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 32,
		"readImmediateBytes": 4
	}
};


oneByteOpcodes = {
	# add r16/32/64 to rm16/32/64
	0x01: {
		"name": "add",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# or rm8 or r8
	0x08:
	{
		"name": "or",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# or rm16/32/64 or r16/32/64
	0x09:
	{
		"name": "or",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True
	},

	# and ax/eax/rax and imm16/32
	0x25: {
		"name": "and",
		"opcodeType": LOGIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"	
	},

	# sub r16/32/64 from rm16/32/64
	0x29: {
		"name": "sub",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# xor rm16/32/64 xor r16/32/64
	0x31: {
		"name": "xor",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True
	},

	# xor r16/32/64 xor rm16/32/64
	0x33: {
		"name": "xor",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False,
	},

	# cmp r16/32/64 with rm16/32/64
	0x39: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# cmp rm16/32/64 with r16/32/64
	0x3b: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cmp imm8 with al
	0x3c: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1,
		"autoInsertRegister": "000"
	},

	# cmp imm16/32 with ax/eax/rax
	0x3d: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"
	},

	# movsxd r64 -> rm32 with rex.w
	0x63: {
		"name": "movsxd",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# imul r16/32/64 <- rm16/32/64 * imm8
	0x6b: {
		"name": "imul",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# jb rel8
	0x72: jumpDetails("jb"),

	# je rel8
	0x73: jumpDetails("jae"),

	# je rel8
	0x74: jumpDetails("je"),

	# jne rel8
	0x75: jumpDetails("jne"),

	# jbe rel8
	0x76: jumpDetails("jbe"),

	# ja rel8
	0x77: jumpDetails("ja"),

	# js rel8
	0x78: jumpDetails("js"),

	# js rel8
	0x79: jumpDetails("jns"),

	# jl rel8
	0x7c: jumpDetails("jl"),

	# jle rel8 
	0x7e: jumpDetails("jle"),

	# jg rel8 
	0x7f: jumpDetails("jg"),

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm8 -> rm8
	0x80: {
		"name": ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"],
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm32 -> rm16/32/64
	0x81: {
		"name": ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 4
	},

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm8 -> rm16/32/64
	0x83: {
		"name": ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# test r8 and rm8
	0x84: {
		"name": "test",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# test r16/32/64 and rm16/32/64
	0x85: {
		"name": "test",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# mov r8 -> rm/8
	0x88: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# mov rm16/32/64 -> r16/32/64
	0x89: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True
	},

	# mov r16/32/64 -> rm16/32/64
	0x8b: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# lea r16/32/64 <- rm
	0x8d: {
		"name": "lea",
		"opcodeType": MISC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cdqe
	0x98: {
		"name": "cdqe",
		"opcodeType": TRANSFER_TYPE
	},

	# nop
	0x90: {
		"name": "nop",
		"opcodeType": MISC_TYPE
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate rm8 by imm8
	0xc0: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate rm16/32/64 by imm8
	0xc1: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# return near
	0xc3: {
		"name": "ret",
		"opcodeType": JUMP_TYPE
	},

	# mov /0 imm8 -> rm8
	0xc6: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# mov /0 imm16/32/64 -> rm16/32/64
	0xc7: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 4
	},

	# leave
	0xc9: {
		"name": "leave",
		"opcodeType": JUMP_TYPE
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate cl by rm16/32/64
	0xd3: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"autoInsertRegister": "001"
	},

	# call near rel16/32
	0xe8: {
		"name": "call",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 4
	},
	
	# jmp rel16/32
	0xe9: {
		"name": "jmp",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 4
	},

	# jmp rel8
	0xeb: {
		"name": "jmp",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 1
	},

	# test/test/not/neg/mul/imul/div/idiv
	# rm16/32/64
	0xf7: {
		"name": ["test", "test", "not", "neg", "mul", "imul", "div", "idiv"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True
	},

	# inc/dec/call/callf/jmp/jmpf/push
	0xff: {
		"name": ["inc", "dec", "call", "callf", "jmp", "jmpf", "push"],
		"opcodeType": JUMP_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True
	}
};


twoByteOpcodes = {
	# cmovs rm16/32/64 -> r16/32/64
	0x48: {
		"name": "cmovs",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# jae rel32
	0x83: jumpDetails("jae", 4),

	# je rel32
	0x84: jumpDetails("je", 4),

	# jne rel32
	0x85: jumpDetails("jne", 4),
	
	# jbe rel32
	0x86: jumpDetails("jbe", 4),

	# ja rel32
	0x87: jumpDetails("ja", 4),

	# ja rel32
	0x88: jumpDetails("js", 4),

	# jle rel32
	0x8e: jumpDetails("jle", 4),

	# jle rel32
	0x8f: jumpDetails("jg", 4),

	# sete /0 rm8
	0x94: {
		"name": "sete",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 8,
		"opcodeExtension": "True",
		"readModRegRm": True
	},

	# setne /0 rm8
	0x95: {
		"name": "setne",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 8,
		"opcodeExtension": "True",
		"readModRegRm": True
	},

	# imul r16/32/64 <- r16/32/64 * rm16/32/64
	0xaf: {
		"name": "imul",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movzx rm8 -> r16/32/64
	0xb6: {
		"name": "movzx",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movsx rm8 -> r16/32/64
	0xbe: {
		"name": "movsx",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movzx rm16 -> r32/64
	0xb7: {
		"name": "movzx",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},
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
		if (str(type(opcodeType)) != "<type 'int'>"):
			print(opcodeType);
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