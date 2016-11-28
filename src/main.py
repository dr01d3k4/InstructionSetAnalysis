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


def dotsToUnderscores(filename):
	return filename.replace(".", "_");


def getInputFilename(folder, filename):
	if (folder != ""):
		folder += "/";

	return OBJECT_FILES_ROOT + folder + filename;


def getOutputFilename(folder, filename, skipNopsAfterJumps = False):
	editedFilename = "results_for_";
	editedFilename += dotsToUnderscores(filename);
	if (skipNopsAfterJumps):
		editedFilename += "_nop_skip";
	editedFilename += ".txt";

	return getInputFilename(folder, editedFilename);


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


def decodeMachineCode(architecture, machineCode, skipNopsAfterJumps = False, firstByteOffset = 0, startPrintingFrom = -1, instructionLimit = -1):
	# "withDebug" is because this is a tuple of (startByte, [bytesInInstruction], InstructionInstance)
	instructionsWithDebug, nopsSkippedAfterJumps = architecture.decode(machineCode, skipNopsAfterJumps, firstByteOffset, instructionLimit);
	instructions = map(lambda x: x[2], instructionsWithDebug);

	printInstructionsWithDebug(instructionsWithDebug, startPrintingFrom = startPrintingFrom, showInstructionDetails = False);

	return instructions, nopsSkippedAfterJumps;


def calculateStats(architecture, compiler, inputFilename, outputFilename, instructions, nopsSkippedAfterJumps, writeOutput = print):
	return stats.calculateStats(architecture, compiler, inputFilename, outputFilename, instructions, nopsSkippedAfterJumps, writeOutput);


def dissassembleObjectFile(architecture, compiler, filename, skipNopsAfterJumps = False, firstByteOffset = 0, startPrintingFrom = -1, instructionLimit = -1):
	elf64File = readElf64File(filename);
	textSection = getTextSection(elf64File);

	elf64File.setSectionContents(".text", None);
	elf64File = None;
	gc.collect();

	instructions, nopsSkippedAfterJumps = decodeMachineCode(architecture, textSection, skipNopsAfterJumps, firstByteOffset, startPrintingFrom, instructionLimit);
	textSection = None;
	gc.collect();

	return instructions, nopsSkippedAfterJumps;


def outputStatsForObjectFile(architecture, compiler, folder, filename, skipNopsAfterJumps = False):
	inputFilename = getInputFilename(folder, filename);
	outputFilename = getOutputFilename(folder, filename, skipNopsAfterJumps);

	print("-" * 80);
	print("Outputting stats for \"" + filename + "\"");
	print("Input filename: ", inputFilename);
	print("Output filename:", outputFilename);
	print("Skipping nops after jumps:", skipNopsAfterJumps);

	instructions, nopsSkippedAfterJumps = dissassembleObjectFile(architecture, compiler, inputFilename, skipNopsAfterJumps);
	print("");
	print("Instructions decoded");
	print("Total instructions:", len(instructions));
	if (skipNopsAfterJumps):
		print("Nops skipped after jumps: ", nopsSkippedAfterJumps);

	outputFile, writeLine = openFileForWritingLinesClosure(outputFilename);
	stats = calculateStats(architecture, compiler, inputFilename, outputFilename, instructions, nopsSkippedAfterJumps, writeLine);

	print("");
	print("Done, closing file");
	outputFile.close();
	gc.collect();

	print("-" * 80);
	print("");


def printStatsForObjectFile(architecture, compiler, folder, filename, skipNopsAfterJumps = False):
	inputFilename = getInputFilename(folder, filename);

	instructions, nopsSkippedAfterJumps = dissassembleObjectFile(architecture, compiler, inputFilename, skipNopsAfterJumps);
	stats = calculateStats(architecture, compiler, inputFilename, "-", instructions, nopsSkippedAfterJumps, print);


def main():
	x86 = getArchitecture("x86");
	gcc = getCompiler("gcc");
	ghc = getCompiler("ghc");
	clang = getCompiler("clang");

	printingStart = -1;
	instructionLimit = -1; # 1088080;
	skipNopsAfterJumps = True;

	# dissassembleObjectFile(x86, gcc, "object_files/HelloWorld/hello_world_gcc.o", startPrintingFrom = printingStart);
	# dissassembleObjectFile(x86, gcc, "object_files/AddFunction/add_function_gcc.o", startPrintingFrom = printingStart);
	# dissassembleObjectFile(x86, gcc, "object_files/ArrayLoop/array_loop_gcc.o", startPrintingFrom = printingStart);
	
	# dissassembleObjectFile(x86, gcc, "object_files/AddFunction/add_function_linked_gcc.out", skipNopsAfterJumps = skipNopsAfterJumps, firstByteOffset = 0x400490, startPrintingFrom = printingStart);
	# dissassembleObjectFile(x86, clang, "object_files/AddFunction/add_function_linked_clang.out", skipNopsAfterJumps = skipNopsAfterJumps, firstByteOffset = 0x400440, startPrintingFrom = printingStart);

	# outputStatsForObjectFile(x86, gcc, "AddFunction", "add_function_linked_gcc.out");
	# outputStatsForObjectFile(x86, clang, "AddFunction", "add_function_linked_clang.out");

	# dissassembleObjectFile(x86, gcc, "object_files/gcc/gcc_gcc.o", startPrintingFrom = printingStart);

	# dissassembleObjectFile(x86, gcc, "object_files/gcc/gcc_linked_gcc.out", skipNopsAfterJumps = skipNopsAfterJumps, firstByteOffset = 0x4028b0, startPrintingFrom = printingStart);
	
	# dissassembleObjectFile(x86, gcc, "object_files/gcc/gcc_linked_gcc_o3.out", skipNopsAfterJumps = skipNopsAfterJumps, firstByteOffset = 0x402bd0, startPrintingFrom = printingStart, instructionLimit = instructionLimit);
	
	# dissassembleObjectFile(x86, clang, "object_files/gcc/gcc_linked_clang.out", skipNopsAfterJumps = skipNopsAfterJumps, firstByteOffset = 0x402800, startPrintingFrom = printingStart, instructionLimit = instructionLimit);

	# dissassembleObjectFile(x86, clang, "object_files/gcc/gcc_linked_clang_o3.out", skipNopsAfterJumps = skipNopsAfterJumps, firstByteOffset = 0x402850, startPrintingFrom = printingStart, instructionLimit = instructionLimit);

	# outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc.out");
	outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc.out", skipNopsAfterJumps = True);
	# outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang.out");
	outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang.out", skipNopsAfterJumps = True);

	# outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc_o3.out");
	outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc_o3.out", skipNopsAfterJumps = True);
	# outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang_o3.out");
	# outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang_o3.out", skipNopsAfterJumps = True);

	# doWorkOnObjectFile(ghc, x86, "object_files/AddFunction/add_function_ghc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);


main();
# printHexDump("hello_world.o");
# printHexDump("add_function.o");
# printHexDump("array_loop.o");
