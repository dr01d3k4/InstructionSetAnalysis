from __future__ import print_function;
from util.binary_file import printHexDump;
from util.byte_util import bytesToHexString, byteToHexStringSpaceAlign;
import elf64.reader as elf64;
import x86.decoder as x86;
import stats.calculate_stats as stats;
import math;
import gc;
import resource;


# http://stackoverflow.com/questions/32167386/force-garbage-collection-in-python-to-free-memory
showMemoryUsage = False;

def printMemoryUsage():
	if (showMemoryUsage):
		print('Memory usage: % 2.2f MB' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0));


def printInstructionsWithDebug(instructions, showInstructionDetails = False, startPrintingAt = -1):
	if (startPrintingAt < 0):
		# for _, _, instruction in instructions:
		# 	hasOperandToPrint = False;

		# 	for operandType in instruction.getOperandTypes():
		# 		if (operandType[0] >= 5):
		# 			hasOperandToPrint = True;
		# 			break;

		# 	if (hasOperandToPrint):
		# 		print(instruction.toString());

		return;

	print("Starting at:", startPrintingAt);
	print("Last instruction:", len(instructions));
	print("Total printing:", len(instructions) - startPrintingAt);

	if (startPrintingAt > 0):
		instructions = instructions[startPrintingAt:];

	if (len(instructions) == 0):
		print("No instructions");
		return;


	lastInstructionStartByte = instructions[-1][0];
	startByteLength = len(byteToHexStringSpaceAlign(lastInstructionStartByte));

	maxInstructionLength = 0;
	maxOpcodeLength = 0;
	for _, instructionBytes, instruction in instructions:
		instructionLength = len(instructionBytes);
		if (instructionLength > maxInstructionLength):
			maxInstructionLength = instructionLength;

		opcodeLength = len(instruction.getOpcode().name);
		if (opcodeLength > maxOpcodeLength):
			maxOpcodeLength = opcodeLength;

	instructionNumber = max(startPrintingAt, 0);
	for startByte, instructionBytes, instruction in instructions:
		# hasOperandToPrint = False;
		# for operandType in instruction.getOperandTypes():
		# 	if (operandType[0] >= 5):
		# 		hasOperandToPrint = True;
		# 		break;

		# if (not hasOperandToPrint):
		#	instructionNumber += 1;
		#	continue;

		s = "";
		s += "{:4}".format(instructionNumber);
		s += " | ";
		s += byteToHexStringSpaceAlign(startByte, length = startByteLength);
		s += ": ";

		bytesString = bytesToHexString(instructionBytes, bytesBetweenSpaces = 1);
		# 3 because 2 hex chars for 1 byte + 1 space char
		while (len(bytesString) < maxInstructionLength * 3):
			bytesString += " ";

		s += bytesString;
		s += " ";
		s += instruction.toString(maxOpcodeLength);
		print(s);

		if (showInstructionDetails):
			print(repr(instruction));
			if (startByte != lastInstructionStartByte):
				print("-" * 80);

		instructionNumber += 1;


def readElf64File(filename):
	elf64File, errorMessage = elf64.readElf64File(filename);

	if (elf64File == None):
		print("File not loaded: %s" % errorMessage);
		return None;

	# print("File loaded");
	# print(elf64File);

	return elf64File;


def getTextSection(elf64File):
	textSection = elf64File.getSectionContents(".text");

	if (textSection == None):
		print("Text section not found in file");
		return None;

	# print("Text section:", bytesToHexString(textSection));

	return textSection;


def decodeMachineCode(architecture, machineCode, startPrintingFrom = -1, startDebugFrom = -1):
	# "withDebug" is because this is a tuple of (startByte, [bytesInInstruction], InstructionInstance)
	instructionsWithDebug = architecture.decode(machineCode, startDebugAt = startDebugFrom);

	printInstructionsWithDebug(instructionsWithDebug, startPrintingAt = startPrintingFrom, showInstructionDetails = False);
	# printInstructionsWithDebug(instructionsWithDebug, showInstructionDetails = True);

	opcodeTypes = architecture.getOpcodeTypes();
	operandTypes = architecture.getOperandTypes();
	instructions = map(lambda x: x[2], instructionsWithDebug);

	return opcodeTypes, operandTypes, instructions;


def calculateStats(architecture, opcodeTypes, operandTypes, instructions):
	return stats.calculateStats(architecture.getArchitectureName(), opcodeTypes, operandTypes, instructions);


def doWorkOnObjectFile(architecture, filename, startPrintingFrom = -1, startDebugFrom = -1):
	printMemoryUsage();
	elf64File = readElf64File(filename);
	printMemoryUsage();
	textSection = getTextSection(elf64File);
	printMemoryUsage();
	elf64File.setSectionContents(".text", None);
	elf64File = None;
	printMemoryUsage();
	gc.collect();
	printMemoryUsage();
	opcodeTypes, operandTypes, instructions = decodeMachineCode(architecture, textSection, startPrintingFrom, startDebugFrom);
	textSection = None;
	gc.collect();
	printMemoryUsage();
	# stats = calculateStats(architecture, opcodeTypes, operandTypes, instructions);


"""
500000 instructions
Before optimizations: 53.1s
After REX optimizations: 51.6s
After commenting out debug print calls: 24.6s
After opcode caching: 22.2s
"""


def main():
	printingStart = 1141732;
	debugStart = -1;

	# doWorkOnObjectFile(x86, "hello_world.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);
	# doWorkOnObjectFile(x86, "add_function.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);
	# doWorkOnObjectFile(x86, "array_loop.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);
	doWorkOnObjectFile(x86, "gcc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);
	printMemoryUsage();


main();
# printHexDump("hello_world.o");
# printHexDump("add_function.o");
# printHexDump("array_loop.o");
