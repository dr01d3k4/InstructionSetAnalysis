from __future__ import print_function;
from register import getRegRegister, getRmRegister, getBaseRegister, getIndexRegister;
from util.byte_util import bytesToHexString, byteToHexString, byteToBinaryString, getDisplayByteString;
from byte_reader import ByteReader;
from instruction import Instruction;
from opcode import Opcode;
import opcodes;
import operand;
import math;
from rex_prefix import RexPrefix, NoRexPrefix;

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
shouldPrintTodo = True;


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
	debugPrint("Scale bits:", getDisplayByteString(scaleBits));
	debugPrint("Index bits:" , getDisplayByteString(indexBits));
	debugPrint("Base bits: ", getDisplayByteString(baseBits));

	scale = 1;
	if (scaleBits == 0b00):
		scale = 1;
	elif (scaleBits == 0b01):
		scale = 2;
	elif (scaleBits == 0b10):
		scale = 4;
	elif (scaleBits == 0b11):
		scale = 8;

	index = getIndexRegister(indexBits, NoRexPrefix(64));
	base = getBaseRegister(baseBits, NoRexPrefix(64));

	return scale, index, base;


def decodeModRegRm(bytes, rexPrefix, rmIsSource = True, regIsOpcodeExtension = False, readImmediateBytes = 0):
	debugPrint("Reading modregrm");
	debugPrint("Rm is source:", str(rmIsSource));
	debugPrint("Reg is opcode extension:", str(regIsOpcodeExtension));
	debugPrint("Rex prefix:", repr(rexPrefix));

	modRegRmByte = bytes.readByte()[0];
	mod, reg, rm = readModRegRmByte(modRegRmByte);

	debugPrint("");
	debugPrint("Byte:", getDisplayByteString(modRegRmByte));
	debugPrint("Mod: ", getDisplayByteString(mod));
	debugPrint("Reg: " , getDisplayByteString(reg));
	debugPrint("Rm:  ", getDisplayByteString(rm));

	regRegister = getRegRegister(reg, rexPrefix);
	rmRegister = getRmRegister(rm, rexPrefix);

	debugPrint("");
	debugPrint("Reg register:", repr(regRegister));
	debugPrint("Rm register: ", repr(rmRegister));
	debugPrint("");

	operands = [ ];

	if (mod == 0b11):
		if (regIsOpcodeExtension):
			operands.append(operand.RegisterOperand(rmRegister));
		else:
			if (rmIsSource):
				operands.append(operand.RegisterOperand(rmRegister));
				operands.append(operand.RegisterOperand(regRegister));
			else:
				operands.append(operand.RegisterOperand(regRegister));
				operands.append(operand.RegisterOperand(rmRegister));

	else:
		# http://wiki.osdev.org/X86-64_Instruction_Encoding#32.2F64-bit_addressing
		# http://wiki.osdev.org/X86-64_Instruction_Encoding#32.2F64-bit_addressing_2

		modDisplacement = 0;
		if (mod == 0b01):
			modDisplacement = readImmediate8Signed(bytes);
		elif (mod == 0b10):
			modDisplacement = readImmediate32Signed(bytes);

		if (mod != 0b00):
			debugPrint("Mod displacement:", getDisplayByteString(modDisplacement));

		rmDisplacement = 0;
		regOperand = None;
		shouldReadRmDisplacement = False;
		if (rm == 0b101):
			if (mod == 0b00):
				shouldReadRmDisplacement = True;
			if (regIsOpcodeExtension):
				shouldReadRmDisplacement = True;
			if (readImmediateBytes > 0):
				todoPrint("Read immediate bytes overriding read rm displacement hack");
				shouldReadRmDisplacement = False;

		if (shouldReadRmDisplacement):
			rmDisplacement = readImmediate32Signed(bytes);
			debugPrint("Rm displacement: ", getDisplayByteString(rmDisplacement));
			regOperand = operand.ImmediateOperand(rmDisplacement);
		else:
			if (readImmediateBytes == 0):
				regOperand = operand.RegisterOperand(regRegister);

	

		rmOperand = None;
		if (rm == 0b100):
			todoPrint("Check handling of SIB is correct in modregrm decoder");

			sibBits = readScaleIndexBaseByte(bytes.readByte()[0]);
			scaleBits = sibBits[0];
			indexBits = sibBits[1];
			baseBits = sibBits[2];

			sib = decodeScaleIndexBaseByte(scaleBits, indexBits, baseBits, rexPrefix);
			scale = sib[0];
			index = sib[1];
			base = sib[2];

			debugPrint("SIB bits:", sibBits);
			debugPrint("SIB:", sib);
			debugPrint("");

			indexIsSP = ((indexBits == 0b100) and (not rexPrefix.getX()));

			if (mod != 0b00):
				if (indexIsSP):
					rmOperand = operand.RegisterDisplacementOperand(base, modDisplacement);
				else:
					rmOperand = operand.ScaleIndexBaseDisplacementOperand(scale, index, base, modDisplacement);
			else:
				if (baseBits == 0b101):
					baseDisplacement = readImmediate32Signed(bytes);
					debugPrint("Base displacement: ", getDisplayByteString(rmDisplacement));
				
					if (indexIsSP):
						rmOperand = operand.ImmediateDisplacementOperand(baseDisplacement);
					else:
						rmOperand = operand.ScaleIndexBaseDisplacementOperand(scale, index, None, baseDisplacement);
						
				else:
					if (indexIsSP):
						rmOperand = operand.RegisterDisplacementOperand(base);
					else:
						rmOperand = operand.ScaleIndexBaseOperand(scale, index, base);
		else:
			if (mod != 0b00):
				rmOperand = operand.RegisterDisplacementOperand(rmRegister, modDisplacement);
			else:
				rmOperand = operand.RegisterDisplacementOperand(rmRegister, 0);

		debugPrint("Reg operand:", repr(regOperand));
		debugPrint("Rm operand: ", repr(rmOperand));

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

	if (readImmediateBytes > 0):
		debugPrint("Reading " + str(readImmediateBytes) + " bytes of immediate");
		immediate = readImmediateSigned(bytes, readImmediateBytes);
		immediateOperand = operand.ImmediateOperand(immediate);

		debugPrint("Immediate:", getDisplayByteString(immediate));
		debugPrint("Operand:  ", repr(immediateOperand));

		operands.append(immediateOperand);

		if (not rmIsSource):
			debugPrint("Rm is not source, flipping operands");
			operands.reverse();

	return operands;


def readRexPrefix(prefixByte, bytes):
	# http://wiki.osdev.org/X86-64_Instruction_Encoding#REX_prefix

	rexPrefix = NoRexPrefix();

	byte = prefixByte;

	if (prefixByte & 0xf0 == 0x40):
		byte, _ = bytes.readByte();
		rexPrefixArray = [False, False, False, False];

		REX_W = 0;
		REX_R = 1;
		REX_X = 2;
		REX_B = 3;

		debugPrint("\tReading REX prefix: " + getDisplayByteString(prefixByte));

		if (prefixByte & 0x08):
			debugPrint("\t\tRead REX.W prefix");
			rexPrefixArray[REX_W] = True;

		if (prefixByte & 0x04 != 0):
			debugPrint("\tRead REX.R prefix");
			rexPrefixArray[REX_R] = True;

		if (prefixByte & 0x02 != 0):
			debugPrint("\tRead REX.X prefix");
			rexPrefixArray[REX_X] = True;

		if (prefixByte & 0x01 != 0):
			debugPrint("\tRead REX.B prefix");
			rexPrefixArray[REX_B] = True;

		rexPrefix = RexPrefix(*rexPrefixArray);

	return rexPrefix, byte;


"""
[bytes] -> [Instruction]
"""
def decodex86(bytes):
	if (type(bytes) != "<class 'x86.byte_reader.ByteReader'>"):
		bytes = ByteReader(bytes);

	byte = 0;
	instructions = [ ];
	bytesRead = [ ];

	while (True):
		bytes.resetCurrentlyRead();

		opcode = None;
		operands = [ ];

		byte, startByte = bytes.readByte();
		if (byte == None):
			break;

		debugPrint("");
		debugPrint("Reading instruction starting at " + getDisplayByteString(startByte));

		rexPrefix, byte = readRexPrefix(byte, bytes);

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
			debugPrint("\tTwo byte opcode");
			byte, _ = bytes.readByte();

			opcodeByte = (opcodeByte << 8) | byte;
			opcodeByteLength = 2;

			if (byte in opcodes.twoByteOpcodes):
				opcodeDetails = opcodes.twoByteOpcodes[byte];
		
		if (opcodeDetails == None):
			print("\tRead unknown byte");
			print("\t\tLocation: \t" + getDisplayByteString(startByte));
			print("\t\tValue: \t\t" + getDisplayByteString(byte));
			print("\t\tBytes read so far: " + bytesToHexString(bytes.currentlyRead, bytesBetweenSpaces = 1));
			break;

		debugPrint("Opcode details = {");
		for key, value in opcodeDetails.iteritems():
			debugPrint("\t", str(key), "=", str(value));
		debugPrint("}");

		debugPrint("");

		hasOpcodeExtension = opcodes.getOpcodeParam(opcodeDetails, "opcodeExtension");
		shouldReadModRegRm = opcodes.getOpcodeParam(opcodeDetails, "readModRegRm");
		rmIsSource = opcodes.getOpcodeParam(opcodeDetails, "rmIsSource")
		readImmediateBytes = opcodes.getOpcodeParam(opcodeDetails, "readImmediateBytes")

		if ("dataSize" in opcodeDetails):
			dataSize = opcodeDetails["dataSize"];
			if ((dataSize != 32) and (dataSize != 64)):
				debugPrint("Unknown data size:", str(dataSize));
			else:
				debugPrint("Setting data size to", str(dataSize));
				rexPrefix.setDataSize(dataSize);

		if (isTop5Bits):
			debugPrint("Reading top 5 bits opcode");

			if (opcodeByteLength > 1):
				todoPrint("Handle top-5-bit-opcode with multi-byte opcodes");

			registerField = opcodeByte & registerMask;
			opcodeByte = opcodeByte & top5BitsMask

			registerOperand = operand.RegisterOperand(getRmRegister(registerField, rexPrefix));
			operands.append(registerOperand);

		if (hasOpcodeExtension):
			debugPrint("Reading opcode extension");

			modRegRmByte = bytes.readByte()[0];
			mod, reg, rm = readModRegRmByte(modRegRmByte);
			opcodeExtension = reg;

		opcode = Opcode(opcodeByte, opcodeExtension);

		if (shouldReadModRegRm):
			debugPrint("Reading modredrm");

			if (hasOpcodeExtension):
				debugPrint("Already read opcode extension so going back");
				bytes.goBack();

			newOperands = decodeModRegRm(bytes, rexPrefix, rmIsSource = rmIsSource, regIsOpcodeExtension = hasOpcodeExtension, readImmediateBytes = readImmediateBytes);

			for newOperand in newOperands:
				operands.append(newOperand);

		if ((readImmediateBytes > 0) and (not shouldReadModRegRm)):
			immediateData = readImmediateSigned(bytes, readImmediateBytes);
			immediateOperand = operand.ImmediateOperand(immediateData);
			operands.append(immediateOperand);
			operands.reverse();

		if (opcode != None):
			instruction = Instruction(opcode, operands);
			instructionBytes = bytes.currentlyRead;

			instructions.append((startByte, instructionBytes, instruction));

			debugPrint("");
			debugPrint("Read instruction:");
			debugPrint(instruction.toString());
			debugPrint("Bytes: " + bytesToHexString(instructionBytes, bytesBetweenSpaces = 1));
			debugPrint("Instruction: " + repr(instruction));
			debugPrint("-" * 80);
		else:
			print("Opcode is None");
			print("\t\tLocation: \t" + getDisplayByteString(startByte));
			print("\t\tValue: \t\t" + getDisplayByteString(byte));
			print("\t\tBytes read so far: " + bytesToHexString(bytes.currentlyRead, bytesBetweenSpaces = 1));
			break;


	return instructions;