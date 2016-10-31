from __future__ import print_function;


def printOpcodesByType(opcodeTypes, opcodesByType):
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


def printTotalsByType(opcodeTypes, totals, displayingFunction = lambda x: x):
	longestTypeNameLength = 0;

	for typeName in opcodeTypes:
		if (len(typeName) > longestTypeNameLength):
			longestTypeNameLength = len(typeName);

	opcodeTypeNameFormat = "{:{width}}";

	prefix = "\t";

	for index, typeName in enumerate(opcodeTypes):
		s = "";
		s += prefix;
		s += str(index);
		s += " ";
		s += opcodeTypeNameFormat.format(typeName, width = longestTypeNameLength);
		s += " = ";
		s += str(displayingFunction(totals[index]));

		print(s);


def calculateStats(architectureName, opcodeTypes, instructions):
	print("");
	print("Calculating stats for instructions using architecture: " + architectureName);

	print("Opcode types");
	for index, typeName in enumerate(opcodeTypes):
		print("\t", index, typeName);

	opcodesByType = map(lambda _: [ ], opcodeTypes);

	totalOpcodes = 0;

	for instruction in instructions:
		opcode = instruction.getOpcode();
		opcodeType = instruction.getOpcodeType();

		opcodesByType[opcodeType].append(opcode);
		totalOpcodes += 1;

	# printOpcodesByType(opcodeTypes, opcodesByType);

	opcodeTypeCounts = map(len, opcodesByType);
	opcodePercentages = map(lambda c: (100.0 / totalOpcodes) * c, opcodeTypeCounts);

	print("");
	print("Total opcodes:", totalOpcodes);
	print("Counts");
	printTotalsByType(opcodeTypes, opcodeTypeCounts);
	print("");
	print("Percentages");
	printTotalsByType(opcodeTypes, opcodePercentages, lambda p: "{:5.2f}%".format(p));

	return None;