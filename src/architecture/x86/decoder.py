from __future__ import print_function;
from architecture.instruction_base import printInstructionsWithDebug;
from util.byte_util import bytesToHexString, byteToHexString, byteToBinaryString, getDisplayByteString;
from util.byte_reader import ByteReader;
from register import getRegRegister, getRmRegister, getBaseRegister, getIndexRegister, getInstructionPointerRegister;
from instruction import Instruction;
from rex_prefix import getRexPrefix, getRexPrefixFromNumber, getNoRexPrefix;
import opcode as opcodes;
import operand
# import math;

"""
http://www.codeproject.com/Articles/662301/x-Instruction-Encoding-Revealed-Bit-Twiddling-fo
http://wiki.osdev.org/X86-64_Instruction_Encoding#ModR.2FM_and_SIB_bytes
https://en.wikibooks.org/wiki/X86_Assembly/X86_Architecture

In x86 manual:
	Volume 2 starts on page 469
	Instruction set contents starts on page 473
	Chapter 2 starts on page 503
	Format used in instruction set reference explained on page 572

http://ref.x86asm.net/
http://ref.x86asm.net/coder32.html
Columns:
	pf 	= prefix
	0f 	= prefix for two byte opcodes
	po 	= primary opcode
	so 	= secondary opcode
	flds 	= opcode fields
	o 	= register/opcode
			r = modr/m byte has register and r/m operands
			number = opcode extension
	op1-4 	= operands

"""

TOP_5_BITS_MASK = 0b1111111111111000;
REGISTER_MASK = 0b111;

MOD_MASK = 0b11000000;
REG_MASK = REGISTER_MASK << 3;
RM_MASK  = REGISTER_MASK << 0;

SCALE_MASK = MOD_MASK;
INDEX_MASK = REG_MASK;
BASE_MASK  = RM_MASK;

SCALES = [1, 2, 4, 8];

# Group 1
LOCK_PREFIX = 0xf0;
REPNE_PREFIX = 0xf2;
REP_PREFIX = 0xf3;

# Group 2
CS_SEGMENT_OVERRIDE = 0x2e;
SS_SEGMENT_OVERRIDE = 0x36;
DS_SEGMENT_OVERRIDE = 0x3e;
ES_SEGMENT_OVERRIDE = 0x26;
FS_SEGMENT_OVERRIDE = 0x64;
GS_SEGMENT_OVERRIDE = 0x65;
# Same as CS and DS segments?
BRANCH_NOT_TAKEN = 0x2e;
BRANCH_TAKEN = 0x3e;

# Group 3
OPERAND_SIZE_OVERRIDE = 0x66;

# Group 4
ADDRESS_SIZE_OVERRIDE = 0x67;

# REX
REX_PREFIX_UPPER_MASK = 0xf0;
REX_PREFIX_LOWER_MASK = 0x0f;
REX_PREFIX_BASE = 0x40;


def twosComplement(n, bits):
	if ((n & (1 << (bits - 1))) != 0):
		n -= (1 << bits);
	return n;


def readImmediateUnsigned(bytes, n):
	byteArray = [ ];
	for _ in xrange(n):
		byteArray.append(bytes.readByte()[0]);

	# x86 is little endian
	byteArray.reverse();

	i = 0;
	for byte in byteArray:
		i += byte;
		i <<= 8;

	i >>= 8;
	return i;


def readImmediateSigned(bytes, n):
	return twosComplement(readImmediateUnsigned(bytes, n), 8 * n);


def readImmediate8Unsigned(bytes):
	return readImmediateUnsigned(bytes, 1);


def readImmediate8Signed(bytes):
	return readImmediateSigned(bytes, 1);


def readImmediate32Signed(bytes):
	return readImmediateSigned(bytes, 4);


def readImmediate32Unsigned(bytes):
	return readImmediateUnsigned(bytes, 4);


def readModRegRmByte(byte):
	mod = (byte & MOD_MASK) >> 6;
	reg = (byte & REG_MASK) >> 3;
	rm = (byte & RM_MASK) >> 0;

	return mod, reg, rm;


def readScaleIndexBaseByte(byte):
	scale = (byte & SCALE_MASK) >> 6;
	index = (byte & INDEX_MASK) >> 3;
	base = (byte & BASE_MASK) >> 0;

	return scale, index, base;


def decodeScaleIndexBaseByte(scaleBits, indexBits, baseBits, rexPrefix):
	scale = SCALES[scaleBits];
	index = getIndexRegister(indexBits, getNoRexPrefix(64));
	base = getBaseRegister(baseBits, getNoRexPrefix(64));

	return scale, index, base;


def decodeModRegRm(bytes, rexPrefix, rmIsSource = True, regIsOpcodeExtension = False, segmentOverride = operand.NO_SEGMENT_OVERRIDE):
	# Page 508 in intel manual
	modRegRmByte = bytes.readByte()[0];
	mod, reg, rm = readModRegRmByte(modRegRmByte);

	regRegister = getRegRegister(reg, rexPrefix);
	rmRegister = getRmRegister(rm, rexPrefix);

	operands = [ ];

	rmOperand = None;
	regOperand = None;

	if (mod == 0b11):
		rmOperand = operand.RegisterOperand(rmRegister);

		if (not regIsOpcodeExtension):
			regOperand = operand.RegisterOperand(regRegister);

	else:
		# Read SIB if rm is 0b100
		sibBits = 0;
		scaleBits = 0;
		indexBits = 0;
		baseBits = 0;
		hasReadSib = False;

		if (rm == 0b100):
			sibBits = readScaleIndexBaseByte(bytes.readByte()[0]);
			scaleBits = sibBits[0];
			indexBits = sibBits[1];
			baseBits = sibBits[2];

			hasReadSib = True;

		# Read displacement after SIB
		# If mod is 00 and rm is 0b101, then the whole operand is just disp32
		# If mod is 01 or 10, read 8/32 bit displacement
		displacement = 0;
		hasReadDisplacement = False;

		if ((mod == 0b00) and (rm == 0b101)):
			# rmRegister = None;
			rmRegister = getInstructionPointerRegister();

			displacement = readImmediate32Signed(bytes);
			hasReadDisplacement = True;

		elif (mod == 0b01):
			displacement = readImmediate8Signed(bytes);
			hasReadDisplacement = True;

		elif (mod == 0b10):
			displacement = readImmediate32Signed(bytes);
			hasReadDisplacement = True;

		if (not hasReadSib):
			if (not hasReadDisplacement):
				if (rmRegister == None):
					print("Rm register is none?");
				else:
					rmOperand = operand.RegisterMemoryOperand(rmRegister, segmentOverride);
			else:
				if (rmRegister == None):
					rmOperand = operand.ImmediateOperand(displacement);
				else:
					rmOperand = operand.RegisterDisplacementOperand(rmRegister, displacement, segmentOverride);
		else:
			sib = decodeScaleIndexBaseByte(scaleBits, indexBits, baseBits, rexPrefix);
			scale = sib[0];
			index = sib[1];
			base = sib[2];

			indexIsSP = ((indexBits == 0b100) and (not rexPrefix.getX()));


			if (mod != 0b00):
				if (indexIsSP):
					rmOperand = operand.RegisterDisplacementOperand(base, displacement, segmentOverride);
				else:
					rmOperand = operand.ScaleIndexBaseDisplacementOperand(scale, index, base, displacement, segmentOverride);
			else:
				if (baseBits == 0b101):
					baseDisplacement = readImmediate32Signed(bytes);
				
					if (indexIsSP):
						rmOperand = operand.ImmediateDisplacementOperand(baseDisplacement, segmentOverride);
					else:
						rmOperand = operand.ScaleIndexBaseDisplacementOperand(scale, index, None, baseDisplacement, segmentOverride);
						
				else:
					if (indexIsSP):
						rmOperand = operand.RegisterMemoryOperand(base, segmentOverride);
					else:
						rmOperand = operand.ScaleIndexBaseOperand(scale, index, base, segmentOverride);

		if (not regIsOpcodeExtension):
			regOperand = operand.RegisterOperand(regRegister);

	if (rmIsSource):
		if (rmOperand != None):
			operands.append(rmOperand);

		if (regOperand != None):
			operands.append(regOperand);

	else:
		if (regOperand != None):
			operands.append(regOperand);
		
		if (rmOperand != None):
			operands.append(rmOperand);

	return operands;


def addPrefixByte(prefixBytes, prefixBytesLength, byte):
	return ((prefixBytes << (8 * prefixBytesLength)) | byte), prefixBytesLength + 1;


def readPrefixBytes(bytes):
	byte = bytes.getCurrentByte();

	group1Prefix = -1;
	group2Prefix = -1;
	group3Prefix = -1;
	group4Prefix = -1;
	rexPrefix = getNoRexPrefix();

	prefixBytes = 0x0;
	prefixBytesLength = 0;

	prefixNames = [ ];

	while (True):
		# Group 1
		if ((byte == LOCK_PREFIX) or (byte == REPNE_PREFIX) or (byte == REP_PREFIX)):
			if (group1Prefix == -1):
				group1Prefix = byte;

			if (byte == REPNE_PREFIX):
				prefixNames.append("repn");
			elif (byte == REP_PREFIX):
				prefixNames.append("rep");

			prefixBytes, prefixBytesLength = addPrefixByte(prefixBytes, prefixBytesLength, byte);
			byte, _ = bytes.readByte();
			continue;

		# Group 2
		if ((byte == CS_SEGMENT_OVERRIDE)
			or (byte == SS_SEGMENT_OVERRIDE)
			or (byte == DS_SEGMENT_OVERRIDE)
			or (byte == ES_SEGMENT_OVERRIDE)
			or (byte == FS_SEGMENT_OVERRIDE)
			or (byte == GS_SEGMENT_OVERRIDE)):

			if (group2Prefix == -1):
				group2Prefix = byte;

			prefixBytes, prefixBytesLength = addPrefixByte(prefixBytes, prefixBytesLength, byte);
			byte, _ = bytes.readByte();
			continue;

		# Group 3
		if (byte == OPERAND_SIZE_OVERRIDE):
			if (group3Prefix == -1):
				group3Prefix = byte;
			else:
				prefixNames.append("data32");

			prefixBytes, prefixBytesLength = addPrefixByte(prefixBytes, prefixBytesLength, byte);
			byte, _ = bytes.readByte();
			continue;

		# Group 3
		if (byte == ADDRESS_SIZE_OVERRIDE):
			if (group3Prefix == -1):
				group3Prefix = byte;

			prefixBytes, prefixBytesLength = addPrefixByte(prefixBytes, prefixBytesLength, byte);
			byte, _ = bytes.readByte();
			continue;

		break;

	if (byte & REX_PREFIX_UPPER_MASK == REX_PREFIX_BASE):
		rexNumber = byte & REX_PREFIX_LOWER_MASK;
		rexPrefix = getRexPrefixFromNumber(rexNumber);

		prefixBytes, prefixBytesLength = addPrefixByte(prefixBytes, prefixBytesLength, byte);
		bytes.readByte();

	prefixString = " ".join(prefixNames);

	return group1Prefix, group2Prefix, group3Prefix, group4Prefix, rexPrefix, prefixBytes, prefixBytesLength, prefixString;


def failDecoding(errorMessage, instructions, startByte, byte, bytes):
	dashLength = 120;
	print("");
	print("-" * dashLength);
	print("\t{:}".format(errorMessage));
	print("\t\tIndex: \t{:}".format(getDisplayByteString(len(instructions))));
	print("\t\tLocation: \t{:}".format(getDisplayByteString(startByte)));
	print("\t\tValue: \t\t{:}".format(getDisplayByteString(byte)));
	print("\t\tBytes read so far: {:}".format(bytesToHexString(bytes.currentlyRead, bytesBetweenSpaces = 1)));
	print("");

	showInstructionHistory = 10; # 8;
	print("Showing previous {:} instruction{:}".format(showInstructionHistory, "s" if showInstructionHistory != 1 else ""));
	startFrom = max(0, len(instructions) - showInstructionHistory);
	printInstructionsWithDebug(instructions, startPrintingFrom = startFrom, showInstructionDetails = False);

	print("-" * dashLength);
	print("");


"""
[bytes] -> [Instruction]
"""
def decode(bytes, skipNopsAfterJumps = False, firstByteOffset = 0, instructionLimit = -1):
	if (type(bytes) is not ByteReader):
		bytes = ByteReader(bytes);

	byte = 0;
	instructions = [ ];
	bytesRead = [ ];

	nopsSkippedAfterJumps = 0;

	opcodesBeforeNops = { };
	showOpcodesBeforeNops = True;

	while (True):
		bytes.resetCurrentlyRead();

		if ((instructionLimit >= 0) and (len(instructions) >= instructionLimit)):
			failDecoding("Reached instruction limit of {:}".format(instructionLimit), instructions, startByte, byte, bytes);
			break;

		opcode = None;
		operands = [ ];

		byte, startByte = bytes.readByte();
		if (byte == None):
			break;

		startByte += firstByteOffset;

		group1Prefix, group2Prefix, group3Prefix, group4Prefix, rexPrefix, prefixBytes, prefixBytesLength, prefixString = readPrefixBytes(bytes);

		segmentOverride = operand.getSegmentOverrideFromPrefix(group2Prefix);
		operandSizeOverride = group3Prefix;
		addressSizeOverride = group4Prefix;
		originalRexPrefix = rexPrefix;

		byte = bytes.getCurrentByte();

		opcodeDetails = None;
		isTop5Bits = False;
		opcodeByte = byte;
		opcodeByteLength = 1;
		opcodeExtension = -1;

		if (byte & TOP_5_BITS_MASK in opcodes.top5BitsOpcodes):
			opcodeDetails = opcodes.top5BitsOpcodes[byte & TOP_5_BITS_MASK];
			isTop5Bits = True;
		elif (byte in opcodes.oneByteOpcodes):
			opcodeDetails = opcodes.oneByteOpcodes[byte];

		elif (byte == 0x0f):
			byte, _ = bytes.readByte();

			opcodeByte = (opcodeByte << 8) | byte;
			opcodeByteLength += 1;

			if (byte & TOP_5_BITS_MASK in opcodes.twoByteTop5BitsOpcodes):
				opcodeDetails = opcodes.twoByteTop5BitsOpcodes[byte & TOP_5_BITS_MASK];
				isTop5Bits = True;

			elif (byte in opcodes.twoByteOpcodes):
				opcodeDetails = opcodes.twoByteOpcodes[byte];
		
		if (opcodeDetails == None):
			failDecoding("Read unknown byte", instructions, startByte, byte, bytes);
			break;

		if ("name" not in opcodeDetails):
			print("No name for opcode", opcodeByte);
			break;

		if ("opcodeType" not in opcodeDetails):
			print("No type for opcode", opcodeByte);
			break;

		opcodeName = opcodeDetails["name"];
		opcodeType = opcodeDetails["opcodeType"];

		hasOpcodeExtension = opcodes.getOpcodeParamOrDefault(opcodeDetails, "opcodeExtension");
		shouldReadModRegRm = opcodes.getOpcodeParamOrDefault(opcodeDetails, "readModRegRm");
		rmIsSource = opcodes.getOpcodeParamOrDefault(opcodeDetails, "rmIsSource");
		readImmediateBytes = opcodes.getOpcodeParamOrDefault(opcodeDetails, "readImmediateBytes");
		autoInsertRegister = opcodes.getOpcodeParamOrDefault(opcodeDetails, "autoInsertRegister");
		immediateCanBe64WithRexW = opcodes.getOpcodeParamOrDefault(opcodeDetails, "immediateCanBe64WithRexW");

		autoOperands = opcodes.getOpcodeParamOrDefault(opcodeDetails, "autoOperands");
		for autoOperand in autoOperands:
			operands.append(autoOperand);

		autoImmediateOperands = opcodes.getOpcodeParamOrDefault(opcodeDetails, "autoImmediateOperands");

		if (hasOpcodeExtension and not shouldReadModRegRm):
			failDecoding("{:} {:} has opcode extension but not reading modregrm".format(hex(opcodeByte), opcodeName), instructions, startByte, byte, bytes);

		if ("dataSize" in opcodeDetails):
			dataSize = opcodeDetails["dataSize"];
			rexPrefix = rexPrefix.withDataSize(dataSize);

		if (isTop5Bits):
			registerField = opcodeByte & REGISTER_MASK;
			opcodeByte = opcodeByte & TOP_5_BITS_MASK

			registerOperand = operand.RegisterOperand(getRmRegister(registerField, rexPrefix));
			operands.append(registerOperand);

		if (hasOpcodeExtension):
			modRegRmByte = bytes.readByte()[0];
			mod, reg, rm = readModRegRmByte(modRegRmByte);

			opcodeExtension = reg;

			if (type(opcodeName) is list):
				opcodeName = opcodeName[opcodeExtension];

			if (type(opcodeType) is list):
				opcodeType = opcodeType[opcodeExtension];

		if (opcodeName == ""):
			failDecoding("Opcode name is empty", instructions, startByte, byte, bytes);
			break;

		if (len(prefixString) > 0):
			opcodeName = prefixString + " " + opcodeName;

		opcode = opcodes.getOpcode(opcodeByte, opcodeExtension, opcodeName, opcodeType);

		if (shouldReadModRegRm):
			if (hasOpcodeExtension):
				bytes.goBack();

			newOperands = decodeModRegRm(bytes, rexPrefix, rmIsSource = rmIsSource, regIsOpcodeExtension = hasOpcodeExtension, segmentOverride = segmentOverride);

			for newOperand in newOperands:
				operands.append(newOperand);

		if (autoInsertRegister):
			operands.append(operand.RegisterOperand(getRmRegister(int(autoInsertRegister, 2), rexPrefix)));

		if (type(readImmediateBytes) == list):
			readImmediateBytes = readImmediateBytes[opcodeExtension];
			
		if (readImmediateBytes > 0):
			if (immediateCanBe64WithRexW):
				if (originalRexPrefix.getW()):
					readImmediateBytes = 8;

			if ((operandSizeOverride >= 0) and (readImmediateBytes != 1)):
				readImmediateBytes = 2;

			immediateData = readImmediateSigned(bytes, readImmediateBytes);
			immediateOperand = operand.ImmediateOperand(immediateData);
			operands.append(immediateOperand);

		for autoImmediateOperand in autoImmediateOperands:
			operands.append(operand.ImmediateOperand(autoImmediateOperand));

		if (opcode != None):
			if (skipNopsAfterJumps):
				opcodeNumber = opcode.opcode;
				# Current opcode is a nop
				if ((opcodeNumber == 0x90) or (opcodeNumber == 0x0f1f)):
					# Look at previous instruction
					if (len(instructions) > 0):
						previousInstruction = instructions[-1][2];
						previousOpcode = previousInstruction.getOpcode();
						prevOpcodeNumber = previousOpcode.opcode;

						# Is previous halt, unconditional jump or return
						if ((prevOpcodeNumber == 0xc3) # ret
							or (prevOpcodeNumber == 0xe9) # jmp
							or (prevOpcodeNumber == 0xeb) # jmp
							or (prevOpcodeNumber == 0xf4) # hlt
							or (prevOpcodeNumber == 0xff) # jmp
							):
							nopsSkippedAfterJumps += 1;
							continue;
						else:
							if (previousOpcode in opcodesBeforeNops):
								opcodesBeforeNops[previousOpcode] += 1;
							else:
								opcodesBeforeNops[previousOpcode] = 1;
							# print(repr(previousOpcode));

			instruction = Instruction(prefixBytes, opcode, operands);
			instructionBytes = bytes.currentlyRead;

			instructionTuple = (startByte, instructionBytes, instruction);

			instructions.append(instructionTuple);
		else:
			failDecoding("Opcode is None", instructions, startByte, byte, bytes);
			break;

	if (showOpcodesBeforeNops and (len(opcodesBeforeNops) > 0)):
		if (len(opcodesBeforeNops) > 500):
			print("# of opcodes before nops:", len(opcodesBeforeNops));
		else:
			print("Opcodes before nops:");
			sortedOpcodesBeforeNops = sorted(list(opcodesBeforeNops.items()), key = lambda x: x[1], reverse = True);
			for opcode, count in sortedOpcodesBeforeNops:
				print("\t", count, repr(opcode));

	return instructions, nopsSkippedAfterJumps;