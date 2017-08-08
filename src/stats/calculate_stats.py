from __future__ import print_function;
from datetime import datetime;
import time;


WIDTH_FORMATTER = "{:{width}}";

getPercentage = lambda t: (lambda c: (100.0 / t) * c) if (t != 0) else (lambda _: 0);
percentageFormat = lambda p: "{:6.3f}%".format(p)


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


def printByType(types, values, displayingFunction = lambda x: x, writeOutput = print):
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

		writeOutput(s);


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


def printTable(rowNames, columnNames, values, displayingFunction = lambda x: x, showTotalRow = False, showTotalColumn = False, writeOutput = print):
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

	writeOutput(s);



def getCurrentTimeReadable():
	return datetime.now().strftime("%Y/%m/%d %H:%M:%S");


def timeTakenToString(timeTaken):
	timeInSeconds = timeTaken % 60; # int((timeTaken % 60) * 10000) / 10000.0;
	timeInMinutes = int(timeTaken / 60) % 60;
	timeInHours = int((timeTaken / 60) / 60);
	timeInMilliseconds = timeTaken - int(timeTaken);

	timeString = "";
	timeFormat = "{:} {:}{:}";
	formatTime = lambda t, s: (", " if (len(timeString) != 0) else "") + timeFormat.format(t, s, "" if (t == 1) else "s");

	if (timeInHours != 0):
		timeString += formatTime(timeInHours, "hour");

	if (timeInMinutes != 0):
		timeString += formatTime(timeInMinutes, "minute");

	if ((timeInSeconds != 0) or (len(timeString) == 0)):
		timeString += formatTime(timeInSeconds, "second");

	return timeString;


def calculateStats(architecture, compiler, inputFilename, outputFilename, instructions, nopsSkippedAfterJumps, timeTaken, writeOutput = print):
	print("");
	print("Calculating stats");
	writeOutput("Input filename:\t\t{:}".format(inputFilename));
	writeOutput("Output filename:\t{:}".format(outputFilename));
	writeOutput("Architecture:\t\t{:}".format(architecture.getName()));
	writeOutput("Compiler:\t\t{:}".format(compiler.getName()));
	writeOutput("Total instructions:\t{:}".format(len(instructions)));
	writeOutput("Nops skipped:\t\t{:}".format(nopsSkippedAfterJumps));
	writeOutput("");
	# writeOutput("Time taken: \t\t{:}".format(time.strftime("%H:%M:%S", time.gmtime(timeTaken))));
	writeOutput("Time taken:\t\t{:}".format(timeTakenToString(timeTaken)));
	writeOutput("Time per 1000 intrs:\t{:}".format(timeTakenToString(timeTaken / (len(instructions) / 1000.0))));
	writeOutput("Generated at {:}".format(getCurrentTimeReadable()));
	writeOutput("");
	writeOutput(("-") * 120);
	writeOutput("");

	opcodeTypes = architecture.getOpcodeTypes();
	operandTypes = architecture.getOperandTypes();
	dataDirections = architecture.getDataDirections();
	totalActualOpcodes = architecture.getUniqueOpcodeCount();
	totalActualOpcodesByType = architecture.getCountOfUniqueOpcodesForTypes();

	writeOutput("Opcode types");
	for index, typeName in enumerate(opcodeTypes):
		writeOutput("\t{:} {:}".format(index, typeName));

	writeOutput("");
	writeOutput("Total unique opcodes {:}".format(totalActualOpcodes));
	writeOutput("Total actual opcodes by type");
	for index, (typeName, opcodeCount) in enumerate(zip(opcodeTypes, totalActualOpcodesByType)):
		writeOutput("\t{:} {:10} {:}".format(index, typeName, opcodeCount));

	writeOutput("");
	writeOutput("Operand types");
	for index, typeName in enumerate(operandTypes):
		writeOutput("\t{:} {:}".format(index, typeName));

	writeOutput("");
	writeOutput("Data directions");
	for index, direction in enumerate(dataDirections):
		writeOutput("\t{:} {:}".format(index, direction));

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
			uniqueOpcodesByType[opcodeType][opcode] = 1;
			totalUniqueOpcodes += 1;

		for operandType, operand in instruction.getOperandTypes():
			operandsByType[operandType].append(operand);
			operandTypesByOpcodeType[opcodeType].append(operandType);
			totalOperands += 1;


	opcodeTypeCounts = map(len, opcodesByType);
	opcodePercentages = map(getPercentage(totalOpcodes), opcodeTypeCounts);

	uniqueOpcodesComparedToActual = zip(totalActualOpcodesByType, map(len, uniqueOpcodesByType));

	uniqueOpcodesComparedToActualPercentage = map(lambda (total, used): getPercentage(total)(used), uniqueOpcodesComparedToActual);

	operandTypeCounts = map(len, operandsByType);
	operandPercentages = map(getPercentage(totalOperands), operandTypeCounts);

	operandTypesByOpcodeTypeGrouped = [ ];

	for operandTypesForOpcodeType in operandTypesByOpcodeType:
		operandTypesGrouped = [0] * len(operandTypes);

		for operandType in operandTypesForOpcodeType:
			operandTypesGrouped[operandType] += 1;

		operandTypesByOpcodeTypeGrouped.append(operandTypesGrouped);

	operandTypesByOpcodeTypeGroupedTotalPercentage = multimap(getPercentage(totalOperands), operandTypesByOpcodeTypeGrouped);

	operandTypesByOpcodeTypeGroupedRowTotals = getRowTotals(operandTypesByOpcodeTypeGrouped);
	operandTypesByOpcodeTypeGroupedColumnTotals = getColumnTotals(operandTypesByOpcodeTypeGrouped);

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


	writeOutput("");
	writeOutput("Total opcodes: {:}".format(totalOpcodes));
	writeOutput("Counts");
	printByType(opcodeTypes, opcodeTypeCounts, writeOutput = writeOutput);
	writeOutput("");
	writeOutput("Percentages");
	printByType(opcodeTypes, opcodePercentages, percentageFormat, writeOutput = writeOutput);

	writeOutput("");
	writeOutput("Total unique opcodes: {:}".format(totalUniqueOpcodes));
	writeOutput("Counts");
	printByType(opcodeTypes, uniqueOpcodesByType, dictionaryDiplayingFunction(3, newLines = True), writeOutput = writeOutput);

	writeOutput("");
	writeOutput("Total unique opcodes compared to actual opcodes");
	printByType(opcodeTypes, uniqueOpcodesComparedToActual, writeOutput = writeOutput);
	writeOutput("");
	writeOutput("Total unique opcodes compared to actual opcodes percentage");
	printByType(opcodeTypes, uniqueOpcodesComparedToActualPercentage, percentageFormat, writeOutput = writeOutput);

	writeOutput("");
	writeOutput("Total operands: {:}".format(totalOperands));
	writeOutput("Counts");
	printByType(operandTypes, operandTypeCounts, writeOutput = writeOutput);
	writeOutput("");
	writeOutput("Percentages");
	printByType(operandTypes, operandPercentages, percentageFormat, writeOutput = writeOutput);

	writeOutput("");
	writeOutput("Operand types by opcode types");
	printTable(opcodeTypes, operandTypes, operandTypesByOpcodeTypeGrouped, showTotalRow = True, showTotalColumn = True, writeOutput = writeOutput);

	writeOutput("");
	writeOutput("Operand types by opcode types as percentage of total operands");
	printTable(opcodeTypes, operandTypes, operandTypesByOpcodeTypeGroupedTotalPercentage, percentageFormat, showTotalRow = True, showTotalColumn = True, writeOutput = writeOutput);
	
	writeOutput("");
	writeOutput("Operand types by opcode types as percentage of operand type");
	printTable(opcodeTypes, operandTypes, operandTypesByOpcodeTypeGroupedOperandTypePercentage, percentageFormat, showTotalRow = True, showTotalColumn = False, writeOutput = writeOutput);

	writeOutput("");
	writeOutput("Operand types by opcode types as percentage of opcode type");
	printTable(opcodeTypes, operandTypes, operandTypesByOpcodeTypeGroupedOpcodeTypePercentage, percentageFormat, showTotalRow = False, showTotalColumn = True, writeOutput = writeOutput);

	writeOutput("");
	writeOutput("Data direction by opcode type");
	printTable(opcodeTypes, dataDirections, dataDirectionsByType, showTotalRow = True, showTotalColumn = True, writeOutput = writeOutput);

	return None;