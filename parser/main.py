from __future__ import print_function;
from util.binary_file import printHexDump;
from util.byte_util import bytesToHexString, byteToHexStringSpaceAlign;
import elf64.reader as elf64;
import x86.decoder as x86;
import stats.calculate_stats as stats;
import math;


def printInstructionsWithDebug(instructions, showInstructionDetails = False):
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

	for startByte, instructionBytes, instruction in instructions:
		s = "";
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


def decodeMachineCode(architecture, machineCode):
	# "withDebug" is because this is a tuple of (startByte, [bytesInInstruction], InstructionInstance)
	instructionsWithDebug = architecture.decode(machineCode);
	# printInstructionsWithDebug(instructionsWithDebug);

	opcodeTypes = architecture.getOpcodeTypes();
	instructions = map(lambda x: x[2], instructionsWithDebug);

	return opcodeTypes, instructions;


def calculateStats(architecture, opcodeTypes, instructions):
	return stats.calculateStats(architecture.getArchitectureName(), opcodeTypes, instructions);


def doWorkOnObjectFile(architecture, filename):
	elf64File = readElf64File(filename);
	textSection = getTextSection(elf64File);
	opcodeTypes, instructions = decodeMachineCode(architecture, textSection);
	stats = calculateStats(architecture, opcodeTypes, instructions);


def main():
	# doWorkOnObjectFile(x86, "hello_world.o");
	# doWorkOnObjectFile(x86, "add_function.o");
	doWorkOnObjectFile(x86, "array_loop.o");


main();
# printHexDump("hello_world.o");
# printHexDump("add_function.o");
# printHexDump("array_loop.o");