from __future__ import print_function;


WIDTH_FORMATTER = "{:{width}}";

# getPercentage = lambda t: (lambda c: (100.0 / t) * c if t != 0 else 0);
getPercentage = lambda t: (lambda c: (100.0 / t) * c) if (t != 0) else (lambda _: 0);
percentageFormat = lambda p: "{:6.2f}%".format(p)


def transpose(matrix):
	return zip(*matrix);


def multimap(func, data):
	return map(lambda a: map(lambda v: func(v), a), data);


def compose(f, g):
	return lambda x: f(g(x));


def getRowTotals(matrix):
	return map(sum, matrix);


def getColumnTotals(matrix):
	return map(sum, transpose(matrix));


# def printOpcodesByType(opcodeTypes, opcodesByType):
# 	s = "opcodesByType = {";

# 	for index, typeName in enumerate(opcodeTypes):
# 		opcodes = opcodesByType[index];

# 		s += "\n\t" + typeName + " = {";

# 		for opcode in opcodes:
# 			s += "\n\t\t";
# 			s += repr(opcode);
# 			s += ",";

# 		if (len(opcodes) > 0):
# 			s = s[:-1];
# 			s += "\n\t";
# 		else:
# 			s += " ";

# 		s += "},";

# 	if (len(opcodeTypes) > 0):
# 		s = s[:-1];
# 		s += "\n";
# 	else:
# 		s += " ";

# 	s += "}";
# 	print(s);


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


def dictionaryDiplayingFunction(indentLevel = 0, newLines = True):
	indent = "\t" * indentLevel;

	lineStart = "\n" + indent + "\t" if newLines else "";
	keyValueSep = "\t = " if newLines else " = ";
	lineEnd = "," if newLines else ", ";

	def inner(d):
		s = "{";

		if (len(d) > 0):
			for key, value in d.iteritems():
				s += lineStart;
				s += str(key);
				s += keyValueSep;
				s += str(value);
				s += lineEnd;

			if (newLines):
				s += "\n" + indent;
			s += "}";
		else:
			s += " }";
		return s;

	return inner;


def printTable(rowNames, columnNames, values, displayingFunction = lambda x: x, showTotalRow = False, showTotalColumn = False):
	# data = map(lambda a: map(lambda v: str(displayingFunction(v)), a), values);
	# multimap = multimap(lambda v: str(displayingFunction(v)), values);
	display = compose(str, displayingFunction);
	data = multimap(display, values);

	dataToDisplay = [[""] + columnNames];

	for rowName, row in zip(rowNames, data):
		dataToDisplay.append([rowName] + row);

	if (showTotalRow):
		totalRow = ["Total"] + map(display, getColumnTotals(values));

		if (showTotalColumn):
			totalRow.append(display(sum(map(sum, values))));

		dataToDisplay.append(totalRow);

	if (showTotalColumn):
		dataToDisplay[0].append("Total");

		totals = getRowTotals(values);

		for index, value in enumerate(totals):
			dataToDisplay[index + 1].append(display(value));

	colWidths = map(lambda a: max(map(len, a)), transpose(dataToDisplay));

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


def calculateStats(compiler, architecture, instructions):
	print("");
	print("Calculating stats for instructions");
	print("Architecture:", architecture.getName());
	print("Compiler:", compiler.getName());
	print("");

	opcodeTypes = architecture.getOpcodeTypes();
	operandTypes = architecture.getOperandTypes();
	dataDirections = architecture.getDataDirections();
	totalActualOpcodes = architecture.getUniqueOpcodeCount();
	totalActualOpcodesByType = architecture.getCountOfUniqueOpcodesForTypes();

	print("Opcode types");
	for index, typeName in enumerate(opcodeTypes):
		print("\t", index, typeName);

	print("");
	print("Total unique opcodes", totalActualOpcodes);
	print("Total actual opcodes by type");
	for index, (typeName, opcodeCount) in enumerate(zip(opcodeTypes, totalActualOpcodesByType)):
		print("\t", index, typeName, "\t", opcodeCount);

	print("");
	print("Operand types");
	for index, typeName in enumerate(operandTypes):
		print("\t", index, typeName);

	print("");
	print("Data directions");
	for index, direction in enumerate(dataDirections):
		print("\t", index, direction);

	emptyTotals = lambda t: map(lambda _: [ ], t);
	emptyTotalsDict = lambda t: map(lambda _: { }, t);

	opcodesByType = emptyTotals(opcodeTypes);
	operandsByType = emptyTotals(operandTypes);
	operandTypesByOpcodeType = emptyTotals(opcodeTypes);

	uniqueOpcodesByType = emptyTotalsDict(opcodeTypes);
	dataDirectionsByType = map(lambda _: [0] * len(dataDirections), opcodeTypes);

	totalOpcodes = 0;
	totalOperands = 0;

	totalUniqueOpcodes = 0;

	for instruction in instructions:
		opcode = instruction.getOpcode();
		opcodeType = instruction.getOpcodeType();
		dataDirection = instruction.getDataDirection();

		opcodesByType[opcodeType].append(opcode);
		totalOpcodes += 1;

		dataDirectionsByType[opcodeType][dataDirection] += 1;

		if (opcode in uniqueOpcodesByType[opcodeType]):
			uniqueOpcodesByType[opcodeType][opcode] += 1;
		else:
			uniqueOpcodesByType[opcodeType][opcode] = 0;
			totalUniqueOpcodes += 1;

		for operandType, operand in instruction.getOperandTypes():
			operandsByType[operandType].append(operand);
			operandTypesByOpcodeType[opcodeType].append(operandType);
			totalOperands += 1;


	opcodeTypeCounts = map(len, opcodesByType);
	opcodePercentages = map(getPercentage(totalOpcodes), opcodeTypeCounts);

	uniqueOpcodesComparedToActual = zip(totalActualOpcodesByType, map(len, uniqueOpcodesByType));

	operandTypeCounts = map(len, operandsByType);
	operandPercentages = map(getPercentage(totalOperands), operandTypeCounts);

	operandTypesByOpcodeTypeGrouped = [ ];

	for operandTypesForOpcodeType in operandTypesByOpcodeType:
		operandTypesGrouped = [0] * len(operandTypes);

		for operandType in operandTypesForOpcodeType:
			operandTypesGrouped[operandType] += 1;

		operandTypesByOpcodeTypeGrouped.append(operandTypesGrouped);

	operandTypesByOpcodeTypeGroupedTotalPercentage = multimap(getPercentage(totalOperands), operandTypesByOpcodeTypeGrouped);

	operandTypesByOpcodeTypeGroupedRowTotals = getRowTotals(operandTypesByOpcodeTypeGrouped); # map(sum, operandTypesByOpcodeTypeGrouped);
	operandTypesByOpcodeTypeGroupedColumnTotals = getColumnTotals(operandTypesByOpcodeTypeGrouped); # map(sum, transpose(operandTypesByOpcodeTypeGrouped));

	operandTypesByOpcodeTypeGroupedOperandTypePercentage = [
		[
			getPercentage(total)(value)
			for value, total in zip(row, operandTypesByOpcodeTypeGroupedColumnTotals)
		]
		for row in operandTypesByOpcodeTypeGrouped
	];

	operandTypesByOpcodeTypeGroupedOpcodeTypePercentage = [
		[
			getPercentage(total)(value)
			for value in row
		]
		for row, total in zip(operandTypesByOpcodeTypeGrouped, operandTypesByOpcodeTypeGroupedRowTotals)
	];


	print("");
	print("Total opcodes:", totalOpcodes);
	print("Counts");
	printByType(opcodeTypes, opcodeTypeCounts);
	print("");
	print("Percentages");
	printByType(opcodeTypes, opcodePercentages, percentageFormat);

	print("");
	print("Total unique opcodes", totalUniqueOpcodes);
	print("Counts");
	printByType(opcodeTypes, uniqueOpcodesByType, dictionaryDiplayingFunction(3, newLines = False));

	print("");
	print("Total unique opcodes compared to actual opcodes");
	printByType(opcodeTypes, uniqueOpcodesComparedToActual);


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

	print("");
	print("Operand types by opcode types as percentage of total operands");
	printTable(opcodeTypes, operandTypes, operandTypesByOpcodeTypeGroupedTotalPercentage, percentageFormat, showTotalRow = True, showTotalColumn = True);
	
	print("");
	print("Operand types by opcode types as percentage of operand type");
	printTable(opcodeTypes, operandTypes, operandTypesByOpcodeTypeGroupedOperandTypePercentage, percentageFormat, showTotalRow = True, showTotalColumn = False);

	print("");
	print("Operand types by opcode types as percentage of opcode type");
	printTable(opcodeTypes, operandTypes, operandTypesByOpcodeTypeGroupedOpcodeTypePercentage, percentageFormat, showTotalRow = False, showTotalColumn = True);


	print("");
	print("Data direction by opcode type");
	printTable(opcodeTypes, dataDirections, dataDirectionsByType, showTotalRow = True, showTotalColumn = True);

	# for k in operandTypesByOpcodeType:
	# 	print("\t", k);



	# print("");
	# for k in operandTypesByOpcodeTypeGrouped:
	# 	print("\t", k);

	return None;