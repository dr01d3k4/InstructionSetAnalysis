from __future__ import print_function;


def printFunction(functionName, function):
	print("Printing function \"" + functionName + "\"");
	# print("ob:", function["ob"]);
	# print("fl:", function["fl"]);
	print("Config:", function["config"]);
	print("Instructions:");
	for instruction in function["instructions"]:
		print(instruction);


def parseCallgrindOutput(callgrindFileName):
	functions = { };

	with open(callgrindFileName, "r") as callgrindFile:
		functionConfig = {
			"ob": None,
			"fe": None,
			"fi": None,
			"fl": None,
			"fn": None
		};

		callConfig = {
			"cob": None,
			"cfi": None,
			"cfn": None,
			"jfi": None
		};

		callLines = ["calls", "jump", "jcnd"];

		for line in callgrindFile:
			line = line.strip();

			# Skip empty lines
			if (len(line) == 0):
				continue;

			# Skip header
			if (line.startswith("version:")or line.startswith("creator:")
				or line.startswith("pid:") or line.startswith("cmd:")
				or line.startswith("part:") or line.startswith("desc:")
				or line.startswith("positions:") or line.startswith("events:")
				or line.startswith("summary:") or line.startswith("totals:")):
				continue;

			if (line.startswith("ob=")):
				functionConfig["ob"] = line[3:];
				continue;

			if (line.startswith("fl=")):
				functionConfig["fl"] = line[3:];
				continue;

			if (line.startswith("fi=")):
				functionConfig["fi"] = line[3:];
				continue;
				
			if (line.startswith("fe=")):
				functionConfig["fe"] = line[3:];
				continue;

			if (line.startswith("cob=")):
				callConfig["cob"] = line[4:];
				continue;

			if (line.startswith("cfi=")):
				callConfig["cfi"] = line[4:];
				continue;

			if (line.startswith("cfn=")):
				callConfig["cfn"] = line[4:];
				continue;

			if (line.startswith("jfi=")):
				callConfig["jfi"] = line[4:];
				continue;

			if (line.startswith("fn=")):
				functionName = line[3:];
				if (functionName in functions):
					print("Function \"" + functionName + "\" already exists");

				functionConfig["fn"] = functionName;
				functions[functionName] = {
					"config": functionConfig.copy(),
					"instructions": [ ]
				};

				# print("Created function:", functionName, "=", str(functions[functionName]));

				continue;

			if (line.startswith("0x")):
				lineSplit = line.split();

				functionName = functionConfig["fn"];
				if ((functionName != None) and (functionName in functions)):
					functions[functionName]["instructions"].append(lineSplit);
				else:
					pass;
					# print("Read instruction line but no function");

				continue;

			matchedSplit = False;
			for start in callLines:
				if (line.startswith(start + "=")):
					matchedSplit = True;
					lineSplit = line[len(start) + 1:].split();
					lineData = {
						"type": start,
						# "config": callConfig.copy(),
						"data": lineSplit
					};
					if (start == "calls"):
						lineData["config"] = callConfig.copy();
						callConfig = {
							"cob": None,
							"cfi": None,
							"cfn": None,
							"jfi": None
						};

					functionName = functionConfig["fn"];
					if ((functionName != None) and (functionName in functions)):
						functions[functionName]["instructions"].append(lineData);
					else:
						pass;
						# print("Read split line but no function");

					break;

			if (matchedSplit):
				continue;

			print("Reached unknown line");
			print("\"" + line + "\"");
			print("");
			break;

	# if ("main" in functions):
	# 	printFunction("main", functions["main"]);

	return functions;