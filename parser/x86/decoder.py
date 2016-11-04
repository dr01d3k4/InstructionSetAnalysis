from __future__ import print_function;
from register import getRegRegister, getRmRegister, getBaseRegister, getIndexRegister, getInstructionPointerRegister;
from util.byte_util import bytesToHexString, byteToHexString, byteToBinaryString, getDisplayByteString;
from byte_reader import ByteReader;
from instruction import Instruction;
import opcode as opcodes;
import operand
import math;
from rex_prefix import getRexPrefix, getRexPrefixFromNumber, getNoRexPrefix;

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

# Mod-Reg-R/M byte
"""
1 byte (8 bits)
"This byte determines the instruction's operands and the addressing modes relating to them."

Format
MSB 7 6 5 4 3 2 1 0 LSB
Bits 7 6:
	MOD bits
	00 = "Fetch the contents of the address found within the register specified in the R/M section."
		"Two exceptions to this rule are when the R/M bits are set to 100 - that's when the processor switches to SIB addressing and reads the SIB byte, treated next - or 101, when the processor switches to 32-bit displacement mode, which basically means that a 32 bit number is read from the displacement bytes (see figure 1) and then dereferenced. "
	01 = "This is essentialy the same as 00, except that an 8-bit displacement is added to the value before dereferencing."
	10 = "The same as the above, except that a 32-bit displacement is added to the value."
	11 = "Direct addressing mode. Move the value in the source register to the destination register (the Reg and R/M byte will each refer to a register)."
Bits 5 4 3:
	"REG bits. Specifies the register being addressed."
	Also can be used as opcode extension
Bits 2 1 0:
	"R/M bits. Specifies a register or, together with the MOD bits, can indicate displacement or SIB addressing."


modRegRmByte = readByte();
modBits = (modRegRmByte & 0b11000000) >> 6; # modRegRmByte[0:2];
regBits = (modRegRmByte & 0b00111000) >> 3; # modRegRmByte[2:5];
rmBits = modRegRmByte & 0b00000111; # modRegRmByte[5:8];
"""

# Scale-Index-Base byte (SIB)
"""
Format
MSB 7 6 5 4 3 2 1 0 LSB
Bits 7 6:
	Scale bits
	00 = 1 byte
	01 = 2 bytes
	10 = 4 bytes
	11 = 8 bytes
Bits 5 4 3:
	Index bits
	Normally a register
Bits 2 1 0
	Base bits
	Normally a register

Evalutes to be memory[base + (index * scale)]

"""

"""
   0:	55                   	push   %rbp
   1:	48 89 e5             	mov    %rsp,%rbp
   4:	bf 00 00 00 00       	mov    $0x0,%edi
   9:	e8 00 00 00 00       	callq  e <main+0xe>
   e:	b8 00 00 00 00       	mov    $0x0,%eax
  13:	5d                   	pop    %rbp
  14:	c3                   	retq 
"""

top5BitsMask = 0b11111000;
registerMask = 0b111;

modMask = 0b11000000;
regMask = 0b00111000;
rmMask  = 0b00000111;

scaleMask = modMask;
indexMask = regMask;
baseMask  = rmMask;

shouldPrintDebug = False;
shouldPrintTodo = False;


def debugPrint(*args, **kwargs):
	if (shouldPrintDebug):
		print(*args, **kwargs);


def todoPrint(*args, **kwargs):
	if (shouldPrintTodo):
		print("TODO:", *args, **kwargs);


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
	mod = (byte & modMask) >> 6;
	reg = (byte & regMask) >> 3;
	rm = (byte & rmMask) >> 0;

	return mod, reg, rm;


def readScaleIndexBaseByte(byte):
	scale = (byte & scaleMask) >> 6;
	index = (byte & indexMask) >> 3;
	base = (byte & baseMask) >> 0;

	return scale, index, base;


def decodeScaleIndexBaseByte(scaleBits, indexBits, baseBits, rexPrefix):
	# debugPrint("Decoding SIB");
	# debugPrint("Scale bits:", getDisplayByteString(scaleBits));
	# debugPrint("Index bits:" , getDisplayByteString(indexBits));
	# debugPrint("Base bits: ", getDisplayByteString(baseBits));

	scale = 1;
	if (scaleBits == 0b00):
		scale = 1;
	elif (scaleBits == 0b01):
		scale = 2;
	elif (scaleBits == 0b10):
		scale = 4;
	elif (scaleBits == 0b11):
		scale = 8;

	index = getIndexRegister(indexBits, getNoRexPrefix(64));
	base = getBaseRegister(baseBits, getNoRexPrefix(64));

	return scale, index, base;


def decodeModRegRm(bytes, rexPrefix, rmIsSource = True, regIsOpcodeExtension = False, segmentOverride = operand.NO_SEGMENT_OVERRIDE):
	# Page 508 in intel manual

	# debugPrint("Decoding modregrm");
	# debugPrint("Reg is opcode extension:", str(regIsOpcodeExtension));
	# debugPrint("Rex prefix:", repr(rexPrefix));

	modRegRmByte = bytes.readByte()[0];
	mod, reg, rm = readModRegRmByte(modRegRmByte);

	# debugPrint("");
	# debugPrint("Byte:", getDisplayByteString(modRegRmByte));
	# debugPrint("Mod: ", getDisplayByteString(mod));
	# debugPrint("Reg: " , getDisplayByteString(reg));
	# debugPrint("Rm:  ", getDisplayByteString(rm));

	regRegister = getRegRegister(reg, rexPrefix);
	rmRegister = getRmRegister(rm, rexPrefix);

	# debugPrint("");
	# debugPrint("Reg register:", repr(regRegister));
	# debugPrint("Rm register: ", repr(rmRegister));
	# debugPrint("");

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

		# if (hasReadDisplacement):
			# debugPrint("Read displacement: " + getDisplayByteString(displacement));

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

			# debugPrint("SIB bits:", sibBits);
			# debugPrint("SIB:", sib);
			# debugPrint("");

			indexIsSP = ((indexBits == 0b100) and (not rexPrefix.getX()));


			if (mod != 0b00):
				if (indexIsSP):
					rmOperand = operand.RegisterDisplacementOperand(base, displacement, segmentOverride);
				else:
					rmOperand = operand.ScaleIndexBaseDisplacementOperand(scale, index, base, displacement, segmentOverride);
			else:
				if (baseBits == 0b101):
					baseDisplacement = readImmediate32Signed(bytes);
					# debugPrint("Base displacement: ", getDisplayByteString(baseDisplacement));
				
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


def readRexPrefix(prefixByte, bytes):
	# http://wiki.osdev.org/X86-64_Instruction_Encoding#REX_prefix

	rexPrefix = getNoRexPrefix();

	byte = prefixByte;
	prefixByteToReturn = 0x00;

	if (prefixByte & 0xf0 == 0x40):
		prefixByteToReturn = prefixByte;

		byte, _ = bytes.readByte();

		rexNumber = prefixByte & 0x0F;
		rexPrefix = getRexPrefixFromNumber(rexNumber);
		# rexPrefixArray = [False, False, False, False];

		# # wBit = False;
		# # rBit = False;
		# # xBit = False;
		# # bBit = False;

		# REX_W = 0;
		# REX_R = 1;
		# REX_X = 2;
		# REX_B = 3;

		# # debugPrint("\tReading REX prefix: " + getDisplayByteString(prefixByte));

		# if (prefixByte & 0x08):
		# 	# debugPrint("\t\tRead REX.W prefix");
		# 	rexPrefixArray[REX_W] = True;
		# 	# wBit = True;

		# if (prefixByte & 0x04 != 0):
		# 	# debugPrint("\tRead REX.R prefix");
		# 	rexPrefixArray[REX_R] = True;
		# 	# rBit = True;

		# if (prefixByte & 0x02 != 0):
		# 	# debugPrint("\tRead REX.X prefix");
		# 	rexPrefixArray[REX_X] = True;
		# 	# xBit = True;

		# if (prefixByte & 0x01 != 0):
		# 	# debugPrint("\tRead REX.B prefix");
		# 	rexPrefixArray[REX_B] = True;
		# 	# bBit = True;

		# rexPrefix = RexPrefix(*rexPrefixArray);
		# rexPrefix = getRexPrefix(wBit, rBit, xBit, bBit);

	return rexPrefix, byte, prefixByteToReturn;


"""
[bytes] -> [Instruction]
"""
def decode(bytes, startDebugAt = -1):
	global shouldPrintDebug;

	if (type(bytes) != "<class 'x86.byte_reader.ByteReader'>"):
		bytes = ByteReader(bytes);

	byte = 0;
	instructions = [ ];
	bytesRead = [ ];

	if (startDebugAt == 0):
		shouldPrintDebug = True;
	else:
		shouldPrintDebug = False;

	while (True):
		bytes.resetCurrentlyRead();

		if ((not shouldPrintDebug) and (startDebugAt > 0) and (len(instructions) >= startDebugAt)):
			shouldPrintDebug = True;

		opcode = None;
		operands = [ ];

		byte, startByte = bytes.readByte();
		if (byte == None):
			break;

		# debugPrint("Reading instruction #" + str(len(instructions)) + " starting at " + getDisplayByteString(startByte));

		LOCK_PREFIX = 0xf0;
		REPNE_PREFIX = 0xf2;
		REP_PREFIX = 0xf3;
		group1Prefix = -1;

		prefixBytes = 0x0;
		prefixBytesLength = 0;

		if (byte == LOCK_PREFIX):
			group1Prefix = LOCK_PREFIX;
			prefixBytes = prefixBytes | LOCK_PREFIX;
			prefixBytesLength += 1;
			byte, _ = bytes.readByte();

		if (byte == REPNE_PREFIX):
			group1Prefix = REPNE_PREFIX;
			prefixBytes = prefixBytes | REPNE_PREFIX;
			prefixBytesLength += 1;
			byte, _ = bytes.readByte();

		if (byte == REP_PREFIX):
			group1Prefix = REP_PREFIX;
			prefixBytes = prefixBytes | REP_PREFIX;
			prefixBytesLength += 1;
			byte, _ = bytes.readByte();

		segmentOverride = operand.NO_SEGMENT_OVERRIDE;

		if (byte == 0x64):
			# debugPrint("Read FS segment override");
			todoPrint(str(len(instructions)) + " Handle more segment override prefixes");
			segmentOverride = operand.FS_SEGMENT_OVERRIDE;

			prefixBytes = (prefixBytes << (8 * prefixBytesLength)) | 0x64;
			prefixBytesLength += 1;

			byte, _ = bytes.readByte();

		operandSizePrefix = -1;
		if (byte == 0x66):
			operandSizePrefix = 0x66;
			todoPrint(len(instructions), "Read operand size override prefix");
			prefixBytes = (prefixBytes << (8 * prefixBytesLength)) | 0x66;
			prefixBytesLength += 1;
			byte, _ = bytes.readByte();

		originalRexPrefix = None;
		rexPrefix, byte, rexByte = readRexPrefix(byte, bytes);
		originalRexPrefix = rexPrefix;

		if (rexByte != 0):
			prefixBytes = (prefixBytes << (8 * prefixBytesLength)) | rexByte;
			prefixBytesLength += 1;

		opcodeDetails = None;
		isTop5Bits = False;
		opcodeByte = byte;
		opcodeByteLength = 1;
		opcodeExtension = -1;

		if (byte & top5BitsMask in opcodes.top5BitsOpcodes):
			opcodeDetails = opcodes.top5BitsOpcodes[byte & top5BitsMask];
			isTop5Bits = True;
		elif (byte in opcodes.oneByteOpcodes):
			opcodeDetails = opcodes.oneByteOpcodes[byte];

		elif (byte == 0x0f):
			# debugPrint("\tTwo byte opcode");
			byte, _ = bytes.readByte();

			opcodeByte = (opcodeByte << 8) | byte;
			opcodeByteLength += 1;

			if (byte in opcodes.twoByteOpcodes):
				opcodeDetails = opcodes.twoByteOpcodes[byte];
		
		if (opcodeDetails == None):
			dashLength = 120;
			print("");
			print("-" * dashLength);
			print("\tRead unknown byte");
			print("\t\tIndex: \t" + getDisplayByteString(len(instructions)));
			print("\t\tLocation: \t" + getDisplayByteString(startByte));
			print("\t\tValue: \t\t" + getDisplayByteString(byte));
			print("\t\tBytes read so far: " + bytesToHexString(bytes.currentlyRead, bytesBetweenSpaces = 1));
			print("-" * dashLength);
			print("");
			break;

		# debugPrint("Opcode byte: " + getDisplayByteString(opcodeByte));
		# debugPrint("Opcode details = {");
		# for key, value in opcodeDetails.iteritems():
			# debugPrint("\t", str(key), "=", str(value));
		# debugPrint("}");

		# debugPrint("");

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
			print(hex(opcodeByte), opcodeName, " has opcode extension but not reading modregrm");

		if ("dataSize" in opcodeDetails):
			dataSize = opcodeDetails["dataSize"];
			# if ((dataSize != 8) and (dataSize != 16) and (dataSize != 32) and (dataSize != 64)):
			# 	# debugPrint("Unknown data size:", str(dataSize));
			# else:
				# debugPrint("Setting data size to", str(dataSize));
			rexPrefix = rexPrefix.withDataSize(dataSize);

		if (isTop5Bits):
			# debugPrint("Should read top 5 bits opcode");

			if (opcodeByteLength > 1):
				todoPrint("Handle top-5-bit-opcode with multi-byte opcodes");

			registerField = opcodeByte & registerMask;
			opcodeByte = opcodeByte & top5BitsMask

			registerOperand = operand.RegisterOperand(getRmRegister(registerField, rexPrefix));
			operands.append(registerOperand);

		if (hasOpcodeExtension):
			# debugPrint("Should read opcode extension");

			modRegRmByte = bytes.readByte()[0];
			mod, reg, rm = readModRegRmByte(modRegRmByte);

			opcodeExtension = reg;
			# debugPrint("Opcode extension: " + getDisplayByteString(opcodeExtension));

			if (str(type(opcodeName)) == "<type 'list'>"):
				opcodeName = opcodeName[opcodeExtension];

			if (str(type(opcodeType)) == "<type 'list'>"):
				opcodeType = opcodeType[opcodeExtension];

		if (opcodeName == ""):
			print(len(instructions), "Opcode name is empty");

		if (group1Prefix == REPNE_PREFIX):
			# movsd
			# if ((opcodeByte != 0x0f10) and (opcodeByte != 0x0f11)):
			if (opcodeByte == 0xae):
				opcodeName = "repnz " + opcodeName;

		elif (group1Prefix == REP_PREFIX):
			opcodeName = "rep " + opcodeName;
			# opcodeByte = opcodeByte | (REPNE_PREFIX << (8 * opcodeByteLength));
			# opcodeByteLength += 1;

		# opcode = opcodes.Opcode(opcodeByte, opcodeExtension, opcodeName, opcodeType);
		opcode = opcodes.getOpcode(opcodeByte, opcodeExtension, opcodeName, opcodeType);

		if (shouldReadModRegRm):
			# debugPrint("Should read modredrm");

			if (hasOpcodeExtension):
				# debugPrint("Already read opcode extension so going back");
				bytes.goBack();

			newOperands = decodeModRegRm(bytes, rexPrefix, rmIsSource = rmIsSource, regIsOpcodeExtension = hasOpcodeExtension, segmentOverride = segmentOverride);

			for newOperand in newOperands:
				operands.append(newOperand);

		if (autoInsertRegister):
			operands.append(operand.RegisterOperand(getRmRegister(int(autoInsertRegister, 2), rexPrefix)));

		if (readImmediateBytes > 0):
			if (immediateCanBe64WithRexW):
				if (originalRexPrefix.getW()):
					readImmediateBytes = 8;

			if ((operandSizePrefix >= 0) and (readImmediateBytes != 1)):
				todoPrint(str(len(instructions)) + " Handle operand/address size overide");
				readImmediateBytes = 2;

			# debugPrint("Should read " + str(readImmediateBytes) + " read immediate bytes");
			immediateData = readImmediateSigned(bytes, readImmediateBytes);
			immediateOperand = operand.ImmediateOperand(immediateData);
			operands.append(immediateOperand);

		for autoImmediateOperand in autoImmediateOperands:
			operands.append(operand.ImmediateOperand(autoImmediateOperand));

		if (opcode != None):
			instruction = Instruction(prefixBytes, opcode, operands);
			instructionBytes = bytes.currentlyRead;

			instructionTuple = (startByte, instructionBytes, instruction);

			instructions.append(instructionTuple);

			# if (opcodeByte == 0x0f10):
			# 	print(instructionTuple);

			# if (group1Prefix != -1):
			# 	print(instructionTuple);

			# debugPrint("");
			# debugPrint("Read instruction:");
			# debugPrint(instruction.toString());
			# debugPrint("Bytes: " + bytesToHexString(instructionBytes, bytesBetweenSpaces = 1));
			# debugPrint("Instruction: " + repr(instruction));
			# debugPrint("-" * 80);
		else:
			print("Opcode is None");
			print("\t\tIndex: \t" + getDisplayByteString(len(instructions)));
			print("\t\tLocation: \t" + getDisplayByteString(startByte));
			print("\t\tValue: \t\t" + getDisplayByteString(byte));
			print("\t\tBytes read so far: " + bytesToHexString(bytes.currentlyRead, bytesBetweenSpaces = 1));
			print("");
			break;

		# debugPrint("");

		# if (len(instructions) > 500000):
		# 	break;

	return instructions;


def getArchitectureName():
	return "x86";


def getOpcodeTypes():
	return opcodes.OPCODE_TYPES;


def getOperandTypes():
	return operand.OPERAND_TYPES;