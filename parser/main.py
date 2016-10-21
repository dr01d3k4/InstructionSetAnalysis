from __future__ import print_function;
from util.binary_file import printHexDump;
from elf64.reader import readElf64File;
from util.byte_util import bytesToHexString, byteToHexStringSpaceAlign;
from x86.decoder import decodex86;
import math;


"""
https://0xax.gitbooks.io/linux-insides/content/Theory/ELF.html

https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h

https://uclibc.org/docs/elf-64-gen.pdf

http://www.skyfree.org/linux/references/ELF_Format.pdf
"""


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

	instructions = decodex86(textContents);

	print("");
	print("Decoded");
	if (len(instructions) > 0):
		lastInstructionStartByte = instructions[-1].startByte;
		startByteLength = len(byteToHexStringSpaceAlign(lastInstructionStartByte));

		maxInstructionLength = 0;
		maxOpcodeLength = 0;
		for instruction in instructions:
			instructionLength = len(instruction.bytes);
			if (instructionLength > maxInstructionLength):
				maxInstructionLength = instructionLength;

			opcodeLength = len(instruction.opcode.name);
			if (opcodeLength > maxOpcodeLength):
				maxOpcodeLength = opcodeLength;

		for instruction in instructions:
			instructionString = instruction.toString(startByteLength, maxInstructionLength, maxOpcodeLength);
			print(instructionString);

	else:
		print("No instructions");

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