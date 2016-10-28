from __future__ import print_function;

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


def getOpcodeType(opcode):
	print("Getting type for opcode", opcode);

	number = opcode.opcode;
	extension = opcode.extension;

	opcodeType = -1;

	if (number == 0x50):
		opcodeType = TRANSFER_TYPE;
	elif (number == 0x58):
		opcodeType = TRANSFER_TYPE;
	elif (number == 0xb8):
		opcodeType = TRANSFER_TYPE;
	elif (number == 0x00):
		opcodeType = MISC_TYPE;
	elif (number == 0x01):
		opcodeType = ARITHMETIC_TYPE;
	elif (number == 0x83):
		opcodeType = ARITHMETIC_TYPE;
	elif (number == 0x89):
		opcodeType = TRANSFER_TYPE;
	elif (number == 0x8b):
		opcodeType = TRANSFER_TYPE;
	elif (number == 0xc7):
		opcodeType = TRANSFER_TYPE;
	elif (number == 0x63):
		opcodeType = TRANSFER_TYPE;

	if (opcodeType < 0):
		print("Type unknown for opcode", opcode);
		return None;

	return opcodeType;