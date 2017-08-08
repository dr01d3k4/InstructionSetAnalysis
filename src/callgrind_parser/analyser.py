from __future__ import print_function;


def splitJumpTimes(jumpTimes):
	# print("Splitting jump times:", jumpTimes);
	if ("/" in jumpTimes):
		return map(int, jumpTimes.split("/"));
	else:
		return [int(jumpTimes), 0];


def callgrindInstructionsToDictionary(callgrindInstructions):
	print("-" * 10);
	print("In callgrind instructions to dictionary");
	hexStrToInt = lambda x: int(x, 16);
	# print(callgrindInstructions[0]);


	import pprint;
	pp = pprint.PrettyPrinter(indent = 4);
	# pp.pprint(callgrindInstructions);

	# Turn the callgrind instructions into an array of just the starting bytes and call data
	# Group calls with their instruction
	instructionArray = [ ];
	i = 0;
	while (i < len(callgrindInstructions)):
		if (type(callgrindInstructions[i]) is list):
			instructionArray.append(hexStrToInt(callgrindInstructions[i][0]));
		elif (type(callgrindInstructions[i]) is dict):
			# newData = callgrindInstructions[i].copy();
			oldData = callgrindInstructions[i];
			callData = oldData["data"];

			i += 1;
			if (i >= len(callgrindInstructions)):
				print("Instruction expected for call but reached end");
				break;

			newData = {
				"jumpTimes": splitJumpTimes(callData[0]),
				"jumpStartByte": hexStrToInt(callData[1]),
				# "location": oldData["config"].copy(),
				"type": oldData["type"],
				"instruction": hexStrToInt(callgrindInstructions[i][0]),
			};
			if ("config" in oldData):
				newData["location"] = oldData["config"].copy();

			instructionArray.append(newData);

		i += 1;

	# print(instructionArray);

	# Turn the above array into a dictionary where starting bytes are keys, next byte or dictionary of call data is value
	instructionsDict = { };
	i = 0;
	while (i < len(instructionArray) - 1):
		# Read a starting byte
		if ((type(instructionArray[i]) is str) or (type(instructionArray[i]) is int)):
			currentNumber = instructionArray[i];
			nextNumber = -1;

			# Look for next byte
			i += 1;
			if ((type(instructionArray[i]) is str) or (type(instructionArray[i]) is int)):
				nextNumber = instructionArray[i];
			elif (type(instructionArray[i]) is dict):
				nextNumber = instructionArray[i]["instruction"];
			else:
				print("Unknown type");

			# Put this into dict
			if (currentNumber in instructionsDict):
				# print(currentNumber, " already exists (Number -> ...), current i:", i, "; type of instructionsDict[currentNumber]:", type(instructionsDict[currentNumber]));
				# If overriding a value, it should be a dictionary already so append to it
				if (type(instructionsDict[currentNumber]) is dict):
					instructionsDict[currentNumber]["next"].append(nextNumber);
					instructionsDict[currentNumber]["data"].append({ });
				else:
					print("instructionsDict[currentNumber] is not dict");
			else:
				instructionsDict[currentNumber] = nextNumber;

		# Read a call
		elif (type(instructionArray[i]) is dict):
			currentData = instructionArray[i];
			currentNumber = instructionArray[i]["instruction"];
			nextNumber = -1;

			i += 1;
			if ((type(instructionArray[i]) is str) or (type(instructionArray[i]) is int)):
				nextNumber = instructionArray[i];
			elif (type(instructionArray[i]) is dict):
				nextNumber = instructionArray[i]["instruction"];
			else:
				print("Unknown type");

			# Either create new dict or if overriding, possibly change existing value to dict, then append to it
			if (currentNumber in instructionsDict):
				# print(currentNumber, " already exists (currently parsing Jump -> ...), current i:", i, "; type of instructionsDict[currentNumber]:", type(instructionsDict[currentNumber]));
				if (type(instructionsDict[currentNumber]) is not dict):
					instructionsDict[currentNumber] = {"next": [instructionsDict[currentNumber]], "data": [{ }]};
				instructionsDict[currentNumber]["next"].append(nextNumber);
				instructionsDict[currentNumber]["data"].append(currentData);

			else:
				instructionsDict[currentNumber] = {"next": [nextNumber], "data": [currentData]};
		else:
			print("Unknown type");
			break;

	# Add the final instruction from the array to the dict
	if (i == len(instructionArray) - 1):
		instructionsDict[instructionArray[i]] = None;

	start = int(callgrindInstructions[0][0], 0);

	print("-" * 10);
	return instructionsDict, start;


def getIntructionsDataForFunction(callgrindFunctions, parsedCallgrindFunctions, functionName):
	if (functionName in parsedCallgrindFunctions):
		return parsedCallgrindFunctions[functionName];
	elif (functionName in callgrindFunctions):
		function = callgrindFunctions[functionName];
		parsedInstructions, start = callgrindInstructionsToDictionary(function["instructions"]);
		parsedCallgrindFunctions[functionName] = {
			"start": start,
			"instructions": parsedInstructions,
			"config": function["config"].copy()
		};

		return parsedCallgrindFunctions[functionName];
	else:
		print("Function \"" + functionName + "\" doesn't exist");
		return { };


WORKING_OBJECT_FILE = "/home/ben/Documents/InstructionSetAnalysis/c/DoubleBranchTest/main";


def doDynamicAnalysisOnFunction(instructionsDict, callgrindFunctions, parsedCallgrindFunctions, functionName):
	print("");
	print("-" * 60);

	currentInstructionsData = getIntructionsDataForFunction(callgrindFunctions, parsedCallgrindFunctions, functionName);
	callgrindInstructionDict = currentInstructionsData["instructions"];
	programCounter = currentInstructionsData["start"];

	dynamicInstructions = [ ];
	terminateOn = [ ];

	internalCalledFunctions = [ ];
	externalCalledFunctions = [ ];

	i = 0;
	while (True):
		i += 1;
		limit = 1000;
		if (i > limit):
			print("Reached i >=", limit);
			break;

		if ((programCounter is None) or (not programCounter in callgrindInstructionDict) or (not programCounter in instructionsDict)):
			print("Program counter is none or not in dicts", programCounter, hex(programCounter));
			print("Program counter in callgrindInstructionDict: ", programCounter in callgrindInstructionDict);
			print("Program counter in instructionDict: ", programCounter in instructionsDict);
			print("Program counter:", programCounter, hex(programCounter));
			print("Callgrind line:", callgrindLine);
			break;

		callgrindLine = callgrindInstructionDict[programCounter];
		instruction = instructionsDict[programCounter][1];

		if ((len(dynamicInstructions) > 0) and (dynamicInstructions[-1][0] == programCounter)):
			pass;
		else:
			dynamicInstructions.append((programCounter, instruction));

		if (callgrindLine is None):
			print("Callgrind line is null");
			break;

		if (programCounter in terminateOn):
			print("-" * 20);
			print("Forced terminate");
			print("Program counter:", programCounter, hex(programCounter));
			print("Callgrind line:", callgrindLine);
			print("-" * 20);
			break;

		if (type(callgrindLine) is int):
			programCounter = callgrindLine;
			continue;

		elif (type(callgrindLine) is dict):
			if ("internalPointer" not in callgrindLine):
				callgrindLine["internalPointer"] = 0;

			if (callgrindLine["internalPointer"] >= len(callgrindLine["data"])):
				callgrindLine["internalPointer"] = 0;
				programCounter = callgrindLine["next"][-1];
				continue;

			data = callgrindLine["data"][callgrindLine["internalPointer"]];
			nextInstruction = callgrindLine["next"][callgrindLine["internalPointer"]];

			if (len(data) == 0):
				newProgramCounter = nextInstruction;
			else:

				if ("location" in data):
					targetObjectFile = data["location"]["cob"];

					callDict = data["location"].copy();
					callDict["jumpTimes"] = data["jumpTimes"];

					if ((targetObjectFile == WORKING_OBJECT_FILE) or (targetObjectFile == "???") or (targetObjectFile == None)):
						internalCalledFunctions.append(callDict);
					else:
						externalCalledFunctions.append(callDict);
				else:

					jumpTimes = data["jumpTimes"];

					if (jumpTimes[0] > 0):
						jumpTimes[0] -= 1;
						jumpTimes[1] -= 1;
						newProgramCounter = data["jumpStartByte"];
						
					elif (jumpTimes[1] > 0):
						jumpTimes[1] -= 1;
						newProgramCounter = nextInstruction;
					else:
						foundInstruction = -1;
						maxToTry = 20;
						for i in xrange(1, maxToTry):
							if ((programCounter + i) in instructionsDict):
								foundInstruction = programCounter + i;
								break;
						if (foundInstruction != -1):
							newProgramCounter = foundInstruction;
						else:
							break;

			if (newProgramCounter != programCounter):
				callgrindLine["internalPointer"] = 0;
			else:
				callgrindLine["internalPointer"] += 1;
			programCounter = newProgramCounter;
			continue;
		else:
			print("-" * 20);
			print("Unknown callgrind line", callgrindLine);
			break;

	# print("");
	# print("");
	# print("-" * 100);

	return dynamicInstructions, internalCalledFunctions, externalCalledFunctions;


def doDynamicAnalysis(instructionsWithDebug, callgrindFunctions):
	instructionsDict = {startByte: (len(bytes), instruction) for startByte, bytes, instruction in instructionsWithDebug};
	parsedCallgrindFunctions = { };

	dynamicFunctions = { };

	functionsToAnalyse = ["main"];

	allExternalCalledFunctions = [ ];

	while (len(functionsToAnalyse) > 0):
		functionName = functionsToAnalyse[0];
		del functionsToAnalyse[0];
		print("");
		print("-" * 80);
		print("Doing dynamic analysis on function:", functionName);

		dynamicInstructions, internalCalledFunctions, externalCalledFunctions = doDynamicAnalysisOnFunction(instructionsDict, callgrindFunctions, parsedCallgrindFunctions, functionName);
		print("-" * 40);
		print(functionName, "called internally", internalCalledFunctions);
		print(functionName, "called externally", externalCalledFunctions);

		allExternalCalledFunctions += externalCalledFunctions;

		dynamicFunctions[functionName] = dynamicInstructions;

		for calledFunction in internalCalledFunctions:
			calledName = calledFunction["cfn"];
			calledTimes = calledFunction["jumpTimes"];
			if (calledName not in dynamicFunctions):
				functionsToAnalyse.append(calledName);

	print("");
	print("-" * 80);
	print("All external called functions"); # , allExternalCalledFunctions);
	import pprint;
	pp = pprint.PrettyPrinter(indent = 4);
	pp.pprint(allExternalCalledFunctions);
	
	print("");
	print("-" * 80);

	return dynamicFunctions;
		


# def doDynamicAnalysisOld(instructionsWithDebug, callgrindFunctions):
# 	print("");
# 	print("-" * 100);
# 	if ("main" not in callgrindFunctions):
# 		print("No main in callgrind");
# 		return;

# 	WORKING_OBJECT_FILE = "/home/ben/Documents/InstructionSetAnalysis/c/DoubleBranchTest/main";

# 	instructionsDict = {startByte: (len(bytes), instruction) for startByte, bytes, instruction in instructionsWithDebug};

# 	# print(instructionsDict);
# 	parsedCallgrindFunctions = { };

# 	currentFunctionName = "main";
# 	currentInstructionsData = getIntructionsDataForFunction(callgrindFunctions, parsedCallgrindFunctions, currentFunctionName);
# 	callgrindInstructionDict = currentInstructionsData["instructions"];
# 	programCounter = currentInstructionsData["start"];
# 	stack = [ ];

# 	import pprint;
# 	pp = pprint.PrettyPrinter(indent = 4);
	

# 	# print(instructionsDict);

# 	print("");
# 	print("-" * 100);

# 	# programCounter = int(callgrindFunctions["main"]["instructions"][0][0], 16);
# 	dynamicInstructions = [ ];

# 	terminateOn = [ ]; # 4195744];

# 	# pp.pprint(callgrindInstructionDict);

# 	while (True):
# 		# break; 
# 		if ((programCounter is None) or (not programCounter in callgrindInstructionDict) or (not programCounter in instructionsDict)):
# 			print("Program counter is none or not in dicts", programCounter, hex(programCounter));
# 			print("Program counter in callgrindInstructionDict: ", programCounter in callgrindInstructionDict);
# 			print("Program counter in instructionDict: ", programCounter in instructionsDict);
# 			print("Program counter:", programCounter, hex(programCounter));
# 			print("Callgrind line:", callgrindLine);
# 			break;

# 		callgrindLine = callgrindInstructionDict[programCounter];
# 		instruction = instructionsDict[programCounter][1];

# 		if ((len(dynamicInstructions) > 0) and (dynamicInstructions[-1][0] == programCounter)):
# 			print("Already added instruction");
# 		else:
# 			dynamicInstructions.append((programCounter, instruction));

# 		print("-" * 40);
# 		print("Current program counter:", programCounter, hex(programCounter));
# 		print("Current instruction:", instruction);
# 		if (type(callgrindLine) is int):
# 			print("Current callgrind line:", callgrindLine, hex(callgrindLine));
# 		else:
# 			print("Current callgrind line:", callgrindLine);

# 		if (callgrindLine is None):
# 			print("Callgrind line is null");
# 			print("Stack size:", len(stack));
# 			print("Stack contents:", stack);
# 			if (len(stack) > 0):
# 				print("Going back on stack");
# 				currentFunctionName, programCounter = stack[-1];
# 				del stack[-1];

# 				callgrindInstructionDict = getIntructionsDataForFunction(callgrindFunctions, parsedCallgrindFunctions, currentFunctionName)["instructions"];

# 				print("New program counter:", programCounter, hex(programCounter));
# 				print("Current function name:", currentFunctionName);
# 				print("Stack contents:", stack);

# 				continue;

# 		if (programCounter in terminateOn):
# 			print("-" * 20);
# 			print("Forced terminate");
# 			print("Program counter:", programCounter, hex(programCounter));
# 			print("Callgrind line:", callgrindLine);
# 			print("-" * 20);
# 			break;

# 		# print(type(callgrindLine));

# 		if (type(callgrindLine) is int):
# 			# print("-" * 40);
# 			print("Next is int so going to next");
# 			programCounter = callgrindLine;
# 			print("New program counter:", programCounter, hex(programCounter));
# 			continue;

# 		elif (type(callgrindLine) is dict):
# 			# print("-" * 40);

# 			if ("internalPointer" not in callgrindLine):
# 				callgrindLine["internalPointer"] = 0;

# 			print("Call/jump line on location:", programCounter, "0x%0.2x" % programCounter);
# 			print(callgrindLine);
# 			print("Internal pointer:", callgrindLine["internalPointer"]);

# 			if (callgrindLine["internalPointer"] >= len(callgrindLine["data"])):
# 				print("Pointer out of range");
# 				print("Going to next line");
# 				callgrindLine["internalPointer"] = 0;
# 				programCounter = callgrindLine["next"][-1];
# 				print("New program counter:", programCounter, hex(programCounter));
# 				continue;

# 			data = callgrindLine["data"][callgrindLine["internalPointer"]];
# 			nextInstruction = callgrindLine["next"][callgrindLine["internalPointer"]];

# 			print("Data:", data);
# 			print("Next:", nextInstruction, hex(nextInstruction));

# 			if (len(data) == 0):
# 				print("Data was empty so going to next");

# 				newProgramCounter = nextInstruction;
# 				if (newProgramCounter != programCounter):
# 					callgrindLine["internalPointer"] = 0;
# 				else:
# 					callgrindLine["internalPointer"] += 1;
# 				programCounter = newProgramCounter;

# 				print("New program counter:", programCounter, hex(programCounter));
# 				print("Callgrind line:", callgrindLine);
# 				continue;
# 			else:
# 				print("Data not empty");

# 				if ("location" in data):
# 					print("Data has location");
# 					targetObjectFile = data["location"]["cob"];
# 					print("Target object file:", targetObjectFile);

# 					# if (targetObjectFile == WORKING_OBJECT_FILE):
# 					if ((targetObjectFile == WORKING_OBJECT_FILE) or (targetObjectFile == "???") or (targetObjectFile == None)):
# 						print("Jumping within working object file");
# 						print(data["location"]);
# 						newFunctionName = data["location"]["cfn"];
# 						newInstructionsData = getIntructionsDataForFunction(callgrindFunctions, parsedCallgrindFunctions, newFunctionName);
# 						stack.append([currentFunctionName, programCounter]);
# 						currentFunctionName = newFunctionName;
# 						callgrindInstructionDict = newInstructionsData["instructions"];
# 						programCounter = newInstructionsData["start"];

# 						callgrindLine["internalPointer"] += 1

# 						print("New program counter:", programCounter, hex(programCounter));

# 						continue; # break;

# 					else:
# 						print("Jumping outside working object file so skipping");
						
# 						newProgramCounter = nextInstruction;
# 						if (newProgramCounter != programCounter):
# 							callgrindLine["internalPointer"] = 0;
# 						else:
# 							callgrindLine["internalPointer"] += 1;
# 						programCounter = newProgramCounter;

# 						print("New pc:", programCounter, hex(programCounter));
# 						print("Callgrind line:", callgrindLine);
# 						continue;
# 				else:
# 					print("No location data");

# 					jumpTimes = data["jumpTimes"];
# 					print("Jump times:", jumpTimes);

# 					if (jumpTimes[0] > 0):
# 						print("Jumping to location");
# 						jumpTimes[0] -= 1;
# 						jumpTimes[1] -= 1;
# 						newProgramCounter = data["jumpStartByte"];
						
# 					elif (jumpTimes[1] > 0):
# 						print("Going to next instruction");
# 						jumpTimes[1] -= 1;
# 						newProgramCounter = nextInstruction;
# 					else:
# 						print("Jump times is <= 0");
# 						# print("Going to next instruction");
# 						# jumpTimes[1] -= 1;
# 						# newProgramCounter = nextInstruction;

# 						print("Looking for next instruction");
# 						foundInstruction = -1;
# 						maxToTry = 20;
# 						for i in xrange(1, maxToTry):
# 							if ((programCounter + i) in instructionsDict):
# 								foundInstruction = programCounter + i;
# 								break;
# 						if (foundInstruction != -1):
# 							print("Found:", foundInstruction, hex(foundInstruction));
# 							newProgramCounter = foundInstruction;
# 						else:
# 							print("No instruction found within range of ", programCounter + 1, hex(programCounter + 1), " through to ", programCounter + maxToTry, hex(programCounter + maxToTry));
# 							break;

# 						# break;
# 						# continue;

# 					if (newProgramCounter != programCounter):
# 						callgrindLine["internalPointer"] = 0;
# 					else:
# 						callgrindLine["internalPointer"] += 1;
# 					programCounter = newProgramCounter;

# 					print("New program counter:", programCounter, hex(programCounter));
# 					print("Callgrind line:", callgrindLine);
# 					continue;

# 				break;
# 		else:
# 			print("-" * 20);
# 			print("Unknown callgrind line", callgrindLine);
# 			break;

# 	print("");
# 	print("");
# 	print("-" * 100);

# 	# print("Dynamic instructions:");
# 	# print(dynamicInstructions);

# 	# print("");
# 	# print("");
# 	# print("-" * 100);
# 	# print("Callgrind dict");
# 	# pp.pprint(callgrindInstructionDict);

# 	return dynamicInstructions;