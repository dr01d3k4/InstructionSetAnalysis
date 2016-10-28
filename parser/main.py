from __future__ import print_function;
from util.binary_file import printHexDump;
from elf64.reader import readElf64File;
from util.byte_util import bytesToHexString, byteToHexStringSpaceAlign;
import x86.decoder as x86;
from stats.calculate_stats import calculateStats;
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


def decodeObjectFile(fileLocation):
	print("Working");
	print("");

	elf64FileLocation = fileLocation;
	elf64File, errorMessage = readElf64File(elf64FileLocation);

	if (elf64File == None):
		print("File not loaded: %s" % errorMessage);
		return None;

	print("File loaded");
	# print(elf64File);

	textContents = elf64File.getSectionContents(".text");
	if (textContents == None):
		print("Text contents not found in file");
		return None;

	print("Text contents:", bytesToHexString(textContents));
	print("Decoding");

	# "withDebug" is because this is a tuple of (startByte, [bytesInInstruction], InstructionInstance)
	instructionsWithDebug = x86.decode(textContents);

	print("");
	print("Decoded");
	
	# printInstructionsWithDebug(instructionsWithDebug);

	# Get just the instructions out the tuple
	instructions = map(lambda x: x[2], instructionsWithDebug);

	print("");
	print("Calculating stats");

	opcodeTypes = x86.getOpcodeTypes();

	calculateStats("x86", instructions, opcodeTypes);

	print("");
	print("Done");


def main():
	# decodeObjectFile("hello_world.o");
	# decodeObjectFile("add_function.o");
	decodeObjectFile("array_loop.o");


main();
# printHexDump("hello_world.o");
# printHexDump("add_function.o");
# printHexDump("array_loop.o");