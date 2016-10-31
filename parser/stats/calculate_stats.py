from __future__ import print_function;


def printOpcodesByType(opcodesByType, opcodeTypes):
	s = "opcodesByType = {";

	for index, typeName in enumerate(opcodeTypes):
		opcodes = opcodesByType[index];

		s += "\n\t" + typeName + " = {";

		for opcode in opcodes:
			s += "\n\t\t";
			s += repr(opcode);
			s += ",";

		if (len(opcodes) > 0):
			s = s[:-1];
			s += "\n\t";
		else:
			s += " ";

		s += "},";

	if (len(opcodeTypes) > 0):
		s = s[:-1];
		s += "\n";
	else:
		s += " ";

	s += "}";
	print(s);


def calculateStats(architectureName, instructions, opcodeTypes):
	print("Calculating stats for instructions using architecture: " + architectureName);

	print("Opcode types");
	for index, typeName in enumerate(opcodeTypes):
		print("\t", index, typeName);

	opcodesByType = map(lambda _: [ ], opcodeTypes);
	print(opcodesByType);

	for instruction in instructions:
		opcode = instruction.getOpcode();
		opcodeType = instruction.getOpcodeType();

		opcodesByType[opcodeType].append(opcode);

	printOpcodesByType(opcodesByType, opcodeTypes);

	