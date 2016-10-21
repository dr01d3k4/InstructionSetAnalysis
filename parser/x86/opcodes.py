from util.byte_util import getDisplayByteString;

PUSH = 0x50;

def toString(opcode, opcodeExtension = 0):
	if ((opcodeExtension < 0) or (opcodeExtension > 7)):
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
		return extensions[opcodeExtension];
	elif (opcode == 0x01):
		return "add";
	elif (opcode == PUSH):
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
		return extensions[opcodeExtension];
	elif (opcode == 0x8d):
		return "lea";
	elif (opcode == 0xf7):
		extensions = ["test", "test", "not", "neg", "mul", "imul", "div", "idiv"];
		return extensions[opcodeExtension];
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