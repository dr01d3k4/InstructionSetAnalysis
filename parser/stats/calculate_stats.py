from __future__ import print_function;


WIDTH_FORMATTER = "{:{width}}";


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


def printByType(types, values, displayingFunction = lambda x: x):
	longestTypeNameLength = 0;

	for typeName in types:
		if (len(typeName) > longestTypeNameLength):
			longestTypeNameLength = len(typeName);

	prefix = "\t";

	for index, typeName in enumerate(types):
		s = "";
		s += prefix;
		s += str(index);
		s += " ";
		s += WIDTH_FORMATTER.format(typeName, width = longestTypeNameLength);
		s += " = ";
		s += str(displayingFunction(values[index]));

		print(s);


def printTable(rows, columns, values, displayingFunction = lambda x: x, showTotalRow = False, showTotalColumn = False):
	data = map(lambda a: map(lambda v: str(displayingFunction(v)), a), values);

	dataToDisplay = [[""] + columns];

	for rowName, row in zip(rows, data):
		dataToDisplay.append([rowName] + row);

	if (showTotalRow):
		totalRow = ["Total"] + map(str, map(sum, zip(*values)));

		if (showTotalColumn):
			totalRow.append(str(sum(map(sum, values))));

		dataToDisplay.append(totalRow);

	if (showTotalColumn):
		dataToDisplay[0].append("Total");

		totals = map(sum, values);

		for index, value in enumerate(totals):
			dataToDisplay[index + 1].append(str(value));

	colWidths = map(lambda a: max(map(len, a)), zip(*dataToDisplay));

	HOR_SEP = "|";
	VER_SEP = "-";
	COR_SEP = "+";

	middleLine = (VER_SEP + COR_SEP + VER_SEP).join(map(lambda l: VER_SEP * l, colWidths));

	rowsToDisplay = [ ];
	for row in dataToDisplay:
		dataWithLengths = zip(row, colWidths);
		rowString = " | ".join(map(lambda dataWithLength: WIDTH_FORMATTER.format(dataWithLength[0], width = dataWithLength[1]), dataWithLengths));
		rowsToDisplay.append(rowString);

	s = ("\n" + middleLine + "\n").join(rowsToDisplay);

	print(s);


def calculateStats(architectureName, opcodeTypes, operandTypes, instructions):
	print("");
	print("Calculating stats for instructions using architecture: " + architectureName);

	print("Opcode types");
	for index, typeName in enumerate(opcodeTypes):
		print("\t", index, typeName);

	print("");

	print("Operand types");
	for index, typeName in enumerate(operandTypes):
		print("\t", index, typeName);

	emptyTotals = lambda t: map(lambda _: [ ], t);

	opcodesByType = emptyTotals(opcodeTypes);
	operandsByType = emptyTotals(operandTypes);
	operandTypesByOpcodeType = emptyTotals(opcodeTypes);

	totalOpcodes = 0;
	totalOperands = 0;

	for instruction in instructions:
		opcode = instruction.getOpcode();
		opcodeType = instruction.getOpcodeType();

		opcodesByType[opcodeType].append(opcode);
		totalOpcodes += 1;

		for operandType, operand in instruction.getOperandTypes():
			operandsByType[operandType].append(operand);
			operandTypesByOpcodeType[opcodeType].append(operandType);
			totalOperands += 1;


	getPercentage = (lambda t: lambda c: (100.0 / t) * c);
	percentageFormat = lambda p: "{:5.2f}%".format(p)

	opcodeTypeCounts = map(len, opcodesByType);
	opcodePercentages = map(getPercentage(totalOpcodes), opcodeTypeCounts);

	operandTypeCounts = map(len, operandsByType);
	operandPercentages = map(getPercentage(totalOperands), operandTypeCounts);

	operandTypesByOpcodeTypeGrouped = [ ];

	for operandTypesForOpcodeType in operandTypesByOpcodeType:
		operandTypesGrouped = [0] * len(operandTypes);

		for operandType in operandTypesForOpcodeType:
			operandTypesGrouped[operandType] += 1;

		operandTypesByOpcodeTypeGrouped.append(operandTypesGrouped);


	print("");
	print("Total opcodes:", totalOpcodes);
	print("Counts");
	printByType(opcodeTypes, opcodeTypeCounts);
	print("");
	print("Percentages");
	printByType(opcodeTypes, opcodePercentages, percentageFormat);

	print("");
	print("Total operands:", totalOperands);
	print("Counts");
	printByType(operandTypes, operandTypeCounts);
	print("");
	print("Percentages");
	printByType(operandTypes, operandPercentages, percentageFormat);

	print("");
	print("Operand types by opcode types");

	printTable(opcodeTypes, operandTypes, operandTypesByOpcodeTypeGrouped, showTotalRow = True, showTotalColumn = True);

	# for k in operandTypesByOpcodeType:
	# 	print("\t", k);



	# print("");
	# for k in operandTypesByOpcodeTypeGrouped:
	# 	print("\t", k);

	return None;