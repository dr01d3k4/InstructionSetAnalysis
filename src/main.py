from __future__ import print_function;
from util.binary_file import printHexDump;
import elf64.reader as elf64;
from architecture.instruction_base import printInstructionsWithDebug;
from architecture.architecture import getArchitecture;
from compiler.compiler import getCompiler;
import stats.calculate_stats as stats;
import gc;
from callgrind_parser.parser import parseCallgrindOutput;
from callgrind_parser.analyser import doDynamicAnalysis;
import time;


# 0x8b8b75
"""
500000 instructions
Before optimizations: 53.1s
After REX optimizations: 51.6s
After commenting out debug print calls: 24.6s
After opcode caching: 22.2s
"""


"""
http://www.lttng.org/docs/v2.9/#doc-getting-started
https://github.com/wuyongzheng/pin-instat
http://stackoverflow.com/questions/2971926/tracing-profiling-instructions
https://github.com/jwhitham/x86determiniser
https://lwn.net/Articles/648154/

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


def decodeMachineCodeWithDebug(architecture, machineCode, skipNopsAfterJumps = False, firstByteOffset = 0, startPrintingFrom = -1, instructionLimit = -1):
	# "withDebug" is because this is a tuple of (startByte, [bytesInInstruction], InstructionInstance)
	instructionsWithDebug, nopsSkippedAfterJumps = architecture.decode(machineCode, skipNopsAfterJumps, firstByteOffset, instructionLimit);
	printInstructionsWithDebug(instructionsWithDebug, startPrintingFrom = startPrintingFrom, showInstructionDetails = False);
	return instructionsWithDebug, nopsSkippedAfterJumps;


def decodeMachineCode(architecture, machineCode, skipNopsAfterJumps = False, firstByteOffset = 0, startPrintingFrom = -1, instructionLimit = -1):
	instructionsWithDebug, nopsSkippedAfterJumps = decodeMachineCodeWithDebug(architecture, machineCode, skipNopsAfterJumps, firstByteOffset, startPrintingFrom, instructionLimit);
	instructions = map(lambda x: x[2], instructionsWithDebug);
	return instructions, nopsSkippedAfterJumps;


def calculateStats(architecture, compiler, inputFilename, outputFilename, instructions, nopsSkippedAfterJumps, timeTaken, writeOutput = print):
	return stats.calculateStats(architecture, compiler, inputFilename, outputFilename, instructions, nopsSkippedAfterJumps, timeTaken, writeOutput);


def dissassembleObjectFile(architecture, compiler, filename, skipNopsAfterJumps = False, firstByteOffset = 0, startPrintingFrom = -1, instructionLimit = -1):
	startTime = time.time();

	elf64File = readElf64File(filename);
	textSection = getTextSection(elf64File);

	elf64File.setSectionContents(".text", None);
	elf64File = None;
	gc.collect();

	instructions, nopsSkippedAfterJumps = decodeMachineCode(architecture, textSection, skipNopsAfterJumps, firstByteOffset, startPrintingFrom, instructionLimit);
	textSection = None;
	gc.collect();

	endTime = time.time();
	timeTaken = endTime - startTime;
	return instructions, nopsSkippedAfterJumps, timeTaken;


def dissassembleObjectFileWithDebug(architecture, compiler, filename, skipNopsAfterJumps = False, firstByteOffset = 0, startPrintingFrom = -1, instructionLimit = -1):
	startTime = time.time();

	elf64File = readElf64File(filename);
	textSection = getTextSection(elf64File);

	elf64File.setSectionContents(".text", None);
	elf64File = None;
	gc.collect();

	instructionsWithDebug, nopsSkippedAfterJumps = decodeMachineCodeWithDebug(architecture, textSection, skipNopsAfterJumps, firstByteOffset, startPrintingFrom, instructionLimit);
	textSection = None;
	gc.collect();

	endTime = time.time();
	timeTaken = endTime - startTime;

	return instructionsWithDebug, nopsSkippedAfterJumps, timeTaken;


def outputStatsForObjectFile(architecture, compiler, folder, filename, skipNopsAfterJumps = False):
	inputFilename = getInputFilename(folder, filename);
	outputFilename = getOutputFilename(folder, filename, skipNopsAfterJumps);

	print("-" * 80);
	print("Outputting stats for \"" + filename + "\"");
	print("Input filename: ", inputFilename);
	print("Output filename:", outputFilename);
	print("Skipping nops after jumps:", skipNopsAfterJumps);

	instructions, nopsSkippedAfterJumps, timeTaken = dissassembleObjectFile(architecture, compiler, inputFilename, skipNopsAfterJumps);
	print("");
	print("Instructions decoded");
	print("Total instructions:", len(instructions));
	if (skipNopsAfterJumps):
		print("Nops skipped after jumps: ", nopsSkippedAfterJumps);

	outputFile, writeLine = openFileForWritingLinesClosure(outputFilename);
	stats = calculateStats(architecture, compiler, inputFilename, outputFilename, instructions, nopsSkippedAfterJumps, timeTaken, writeLine);

	print("");
	print("Done, closing file");
	outputFile.close();
	gc.collect();

	print("-" * 80);
	print("");


def printStatsForObjectFile(architecture, compiler, folder, filename, skipNopsAfterJumps = False):
	inputFilename = getInputFilename(folder, filename);

	instructions, nopsSkippedAfterJumps, timeTaken = dissassembleObjectFile(architecture, compiler, inputFilename, skipNopsAfterJumps);
	stats = calculateStats(architecture, compiler, inputFilename, "-", instructions, nopsSkippedAfterJumps, timeTaken, print);


def main():
	x86 = getArchitecture("x86");
	gcc = getCompiler("gcc");
	ghc = getCompiler("ghc");
	clang = getCompiler("clang");

	printingStart = -1;
	instructionLimit = -1; # 1181583;
	skipNopsAfterJumps = False;


	# outputStatsForObjectFile(x86, gcc, "BranchTest", "main", True);
	# printStatsForObjectFile(x86, gcc, "BranchTest", "main", True);

	# instructionsWithDebug, _ = dissassembleObjectFileWithDebug(x86, gcc, "object_files/BranchTest/main", True, firstByteOffset = 0x400440, startPrintingFrom = -1);
	# instructionsWithDebug, _ = dissassembleObjectFileWithDebug(x86, gcc, "object_files/DoubleBranchTest/main", True, firstByteOffset = 0x400490, startPrintingFrom = -1);
	# print(instructionsWithDebug);
	# print("-" * 100);
	# print(instructionsWithDebug);

	# printInstructionsWithDebug(instructionsWithDebug, startPrintingFrom = 0);

	# callgrindFunctions = parseCallgrindOutput("object_files/DoubleBranchTest/CallgrindTestFile.out");
	# dynamicInstructions = map(lambda x: (x[0], [ ], x[1]), doDynamicAnalysis(instructionsWithDebug, callgrindFunctions));
	# dynamicInstructions = doDynamicAnalysis(instructionsWithDebug, callgrindFunctions);

	# printInstructionsWithDebug(dynamicInstructions, startPrintingFrom = 0);
	# printInstructionsWithDebug(map(lambda x: (x[0], [ ], x[1]), dynamicInstructions["main"]), startPrintingFrom = 0);


	# for functionName, data in dynamicInstructions.iteritems():
	# 	code = map(lambda x: (x[0], [ ], x[1]), data);
	# 	print("");
	# 	print("-" * 100);
	# 	print("Dynamic code for function:", functionName);
	# 	printInstructionsWithDebug(code, startPrintingFrom = 0);

	# import pprint;
	# pp = pprint.PrettyPrinter(indent = 4);
	# pp.pprint(dynamicInstructions);



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

	outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc.out");
	outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc.out", skipNopsAfterJumps = True);
	outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang.out");
	outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang.out", skipNopsAfterJumps = True);

	outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc_o3.out");
	outputStatsForObjectFile(x86, gcc, "gcc", "gcc_linked_gcc_o3.out", skipNopsAfterJumps = True);
	outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang_o3.out");
	outputStatsForObjectFile(x86, clang, "gcc", "gcc_linked_clang_o3.out", skipNopsAfterJumps = True);

	# doWorkOnObjectFile(ghc, x86, "object_files/AddFunction/add_function_ghc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);


main();
# printHexDump("hello_world.o");
# printHexDump("add_function.o");
# printHexDump("array_loop.o");
