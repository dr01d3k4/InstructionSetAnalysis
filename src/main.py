from __future__ import print_function;
from util.binary_file import printHexDump;
import elf64.reader as elf64;
from architecture.instruction_base import printInstructionsWithDebug;
from architecture.architecture import getArchitecture;
from compiler.compiler import getCompiler;
import stats.calculate_stats as stats;
import gc;


# 0x8b8b75
"""
500000 instructions
Before optimizations: 53.1s
After REX optimizations: 51.6s
After commenting out debug print calls: 24.6s
After opcode caching: 22.2s
"""


OBJECT_FILES_ROOT = "object_files/";


def getFullFilename(folder, filename):
	if (folder != ""):
		folder += "/";

	return OBJECT_FILES_ROOT + folder + filename;


def getStatsFilename(folder, filename):
	return getFullFilename(folder, "results_for_" + filename + ".txt");


def accumulateLines(lines):
	def inner(line):
		lines.append(line);
	return inner;


def openFileForWritingLinesClosure(filename):
	f = open(filename, "w");

	def writeLine(line):
		f.write(line + "\n");

	return f, writeLine;


def readElf64File(filename):
	elf64File, errorMessage = elf64.readElf64File(filename);

	if (elf64File == None):
		print("File not loaded: %s" % errorMessage);
		return None;

	return elf64File;


def getTextSection(elf64File):
	textSection = elf64File.getSectionContents(".text");

	if (textSection == None):
		print("Text section not found in file");
		return None;

	return textSection;


def decodeMachineCode(architecture, machineCode, firstByteOffset = 0, startPrintingFrom = -1, instructionLimit = -1):
	# "withDebug" is because this is a tuple of (startByte, [bytesInInstruction], InstructionInstance)
	instructionsWithDebug = architecture.decode(machineCode, firstByteOffset, instructionLimit);
	instructions = map(lambda x: x[2], instructionsWithDebug);

	printInstructionsWithDebug(instructionsWithDebug, startPrintingFrom = startPrintingFrom, showInstructionDetails = False);

	return instructions;


def calculateStats(architecture, compiler, filename, instructions, writeOutput = print):
	return stats.calculateStats(architecture, compiler, filename, instructions, writeOutput);


def dissassembleObjectFile(architecture, compiler, filename, firstByteOffset = 0, startPrintingFrom = -1, instructionLimit = -1):
	elf64File = readElf64File(filename);
	textSection = getTextSection(elf64File);

	elf64File.setSectionContents(".text", None);
	elf64File = None;
	gc.collect();

	instructions = decodeMachineCode(architecture, textSection, firstByteOffset, startPrintingFrom, instructionLimit);
	textSection = None;
	gc.collect();

	return instructions;


def outputStatsForObjectFile(architecture, compiler, folder, filename):
	fullFilename = getFullFilename(folder, filename);
	statsFilename = getStatsFilename(folder, filename);

	instructions = dissassembleObjectFile(architecture, compiler, fullFilename);

	outputFile, writeLine = openFileForWritingLinesClosure(statsFilename);
	stats = calculateStats(architecture, compiler, fullFilename, instructions, writeLine);

	outputFile.close();


def printStatsForObjectFile(architecture, compiler, folder, filename):
	fullFilename = getFullFilename(folder, filename);

	instructions = dissassembleObjectFile(architecture, compiler, fullFilename);
	stats = calculateStats(architecture, compiler, fullFilename, instructions, print);


def main():
	x86 = getArchitecture("x86");
	gcc = getCompiler("gcc");
	ghc = getCompiler("ghc");
	clang = getCompiler("clang");

	printingStart = 0; # -1; # 1275290; # 1340; # 9900; # -1; # 1275199;
	instructionLimit = -1; # 626545;

	# dissassembleObjectFile(x86, gcc, "object_files/HelloWorld/hello_world_gcc.o", startPrintingFrom = printingStart);
	# dissassembleObjectFile(x86, gcc, "object_files/AddFunction/add_function_gcc.o", startPrintingFrom = printingStart);
	# dissassembleObjectFile(x86, gcc, "object_files/ArrayLoop/array_loop_gcc.o", startPrintingFrom = printingStart);
	
	# dissassembleObjectFile(x86, gcc, "object_files/AddFunction/add_function_linked_gcc.out", firstByteOffset = 0x400490, startPrintingFrom = printingStart);
	# dissassembleObjectFile(x86, clang, "object_files/AddFunction/add_function_linked_clang.out", firstByteOffset = 0x400440, startPrintingFrom = printingStart);

	# outputStatsForObjectFile(x86, gcc, "AddFunction", "add_function_linked_gcc.out");
	# outputStatsForObjectFile(x86, clang, "AddFunction", "add_function_linked_clang.out");

	# dissassembleObjectFile(x86, gcc, "object_files/gcc/gcc_gcc.o", startPrintingFrom = printingStart);

	# dissassembleObjectFile(x86, gcc, "object_files/gcc/gcc_linked_gcc.out", firstByteOffset = 0x4028b0, startPrintingFrom = printingStart);
	
	# dissassembleObjectFile(x86, clang, "object_files/gcc/gcc_linked_clang.out", firstByteOffset = 0x402800, startPrintingFrom = printingStart, instructionLimit = instructionLimit);

	# outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc.out");
	# outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang.out");

	# doWorkOnObjectFile(ghc, x86, "object_files/AddFunction/add_function_ghc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);


main();
# printHexDump("hello_world.o");
# printHexDump("add_function.o");
# printHexDump("array_loop.o");
