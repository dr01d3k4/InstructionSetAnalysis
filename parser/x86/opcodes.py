from util.byte_util import getDisplayByteString;

PUSH = 0x50;

def toString(opcode, opcodeExtension = 0):
	if ((opcodeExtension < 0) or (opcodeExtension > 7)):
		print("Opcode extension out of bounds");

	if (opcode == PUSH):
		return "push";
	elif (opcode == 0x58):
		return "pop";
	elif ((opcode == 0x89) or (opcode == 0x8b) or (opcode == 0xb8)):
		return "mov";
	elif (opcode == 0xc7):
		return "movl";
	elif (opcode == 0xe8):
		return "callq";
	elif (opcode == 0xc3):
		return "retq";
	elif (opcode == 0x83):
		extensions = ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"];
		return extensions[opcodeExtension];
	elif (opcode == 0xc9):
		return "leaveq";
	elif (opcode == 0x01):
		return "add";
	elif (opcode == 0x63):
		return "movslq";
	else:
		print("Unknown opcode: " + getDisplayByteString(opcode));
		return "";