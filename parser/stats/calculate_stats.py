from __future__ import print_function;


def calculateStats(architectureName, instructions, opcodeTypes):
	print("Calculating stats for instructions using architecture: " + architectureName);

	print("Opcode types");
	for index, typeName in enumerate(opcodeTypes):
		print("\t", index, typeName);

	for instruction in instructions:
		print("");
		
		opcode = instruction.getOpcode();
		opcodeType = opcode.getType();

		if (opcodeType == None):
			print("Type for opcode", opcode, "is none");
			return;

		print("Type for opcode", opcode, "=", opcodeType, opcodeTypes[opcodeType]);
