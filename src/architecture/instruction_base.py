from __future__ import print_function;
import abc;
from util.byte_util import byteToHexStringSpaceAlign;


class InstructionBase(object):
	__metaclass__ = abc.ABCMeta;


	def __init__(self):
		pass;


	@abc.abstractmethod
	def getOpcode(self):
		pass;


	@abc.abstractmethod
	def getOperands(self):
		pass;


	@abc.abstractmethod
	def getOpcodeType(self):
		pass;


	@abc.abstractmethod
	def getOperandTypes(self):
		pass;


	@abc.abstractmethod
	def getDataDirection(self):
		pass;


	@abc.abstractmethod
	def prettyPrint(self, startByte, instructionBytes, instructionNumber, startByteLength, maxInstructionBytesLength, maxOpcodeLength):
		pass;


def printInstructionsWithDebug(instructions, startPrintingFrom = -1, showInstructionDetails = False):
	if (startPrintingFrom < 0):
		return;

	print("Starting at:", startPrintingFrom);
	print("Last instruction:", len(instructions));
	print("Total printing:", len(instructions) - startPrintingFrom);

	if (startPrintingFrom > 0):
		instructions = instructions[startPrintingFrom:];

	if (len(instructions) == 0):
		print("No instructions");
		return;

	lastInstructionStartByte = instructions[-1][0];
	startByteLength = len(byteToHexStringSpaceAlign(lastInstructionStartByte));

	maxInstructionBytesLength = 0;
	maxOpcodeLength = 0;
	for _, instructionBytes, instruction in instructions:
		instructionBytesLength = len(instructionBytes);
		if (instructionBytesLength > maxInstructionBytesLength):
			maxInstructionBytesLength = instructionBytesLength;

		opcodeLength = len(instruction.getOpcode().name);
		if (opcodeLength > maxOpcodeLength):
			maxOpcodeLength = opcodeLength;

	maxMaxOpcodeLength = 6;
	if (maxOpcodeLength > maxMaxOpcodeLength):
		maxOpcodeLength = maxMaxOpcodeLength;

	instructionNumber = max(startPrintingFrom, 0);
	for startByte, instructionBytes, instruction in instructions:
		s = instruction.prettyPrint(startByte, instructionBytes, instructionNumber, startByteLength, maxInstructionBytesLength, maxOpcodeLength);
		print(s);

		if (showInstructionDetails):
			print(repr(instruction));
			if (startByte != lastInstructionStartByte):
				print("-" * 80);

		instructionNumber += 1;