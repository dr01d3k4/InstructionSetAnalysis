from __future__ import print_function;
from register import getRegister;
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

debugPrint = True;


def readModRegRmByte(byte):
	mod = (byte & modMask) >> 6;
	reg = (byte & regMask) >> 3;
	rm = (byte & rmMask) >> 0;

	return mod, reg, rm;


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


def twosComplement(n, bits):
	if ((n & (1 << (bits - 1))) != 0):
		n -= (1 << bits);
	return n;


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


def readRegBottomOpcodeBits(byte, rexPrefix):
	return Opcode(byte & top5BitsMask), operand.RegisterOperand(getRegister(byte & registerMask, rexPrefix));


def decodeModRegRm(bytes, rexPrefix, readRmDisplacement = False, regIsOpcodeExtension = False):
	mod, reg, rm = readModRegRmByte(bytes.readByte()[0]);
	print("Mod:", getDisplayByteString(mod));
	print("Reg:" , getDisplayByteString(reg));
	print("Rm: ", getDisplayByteString(rm));

	operands = [ ];

	if (mod == 0b11):
		regRegister = getRegister(reg, rexPrefix, applyBBit = False);
		operands.append(operand.RegisterOperand(regRegister));

		rmRegister = getRegister(rm, rexPrefix);
		operands.append(operand.RegisterOperand(rmRegister));

	else:
		regRegister = getRegister(reg, rexPrefix, applyBBit = False);
		rmRegister = getRegister(rm, rexPrefix);

		modDisplacement = 0;
		if (mod == 0b00):
			rmOperand = operand.RegisterOperand(rmRegister);
		else:
			if (mod == 0b01):
				modDisplacement = readImmediate8Signed(bytes);

			elif (mod == 0b10):
				modDisplacement = readImmediate32Signed(bytes);

			rmOperand = operand.RegisterDisplacementOperand(rmRegister, modDisplacement);

		if (readRmDisplacement and (rm == 0b101)):
			source = readImmediate32Signed(bytes);
			operands.append(operand.ImmediateOperand(source));
		else:
			operands.append(operand.RegisterOperand(regRegister));

		operands.append(rmOperand);

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

		if (debugPrint):
			print("\tReading REX prefix: " + getDisplayByteString(prefixByte));

		if (prefixByte & 0x08):
			if (debugPrint):
				print("\t\tRead REX.W prefix");
			rexPrefixArray[REX_W] = True;

		if (prefixByte & 0x04 != 0):
			if (debugPrint):
				print("\tRead REX.R prefix");
			rexPrefixArray[REX_R] = True;

		if (prefixByte & 0x02 != 0):
			if (debugPrint):
				print("\tRead REX.X prefix");
			rexPrefixArray[REX_X] = True;

		if (prefixByte & 0x01 != 0):
			if (debugPrint):
				print("\tRead REX.B prefix");
			rexPrefixArray[REX_B] = True;

		rexPrefix = RexPrefix(*rexPrefixArray);
		# rexPrefix = RexPrefix(rexPrefixArray[REX_W], rexPrefixArray[REX_R], rexPrefixArray[REX_X], rexPrefixArray[REX_B]);

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

		if (debugPrint):
			print("");
			print("Reading instruction starting at " + getDisplayByteString(startByte));

		rexPrefix, byte = readRexPrefix(byte, bytes);
		print("Next byte: " + getDisplayByteString(byte));

		if (byte == 0x01):
			# add r to rm
			opcode = Opcode(byte);
			operands = decodeModRegRm(bytes, rexPrefix);

		elif (byte == 0x83):
			# add/or/adc/sbb/and/sub/xor/cmp
			# imm8 to r/m16/32
			mod, reg, rm = readModRegRmByte(bytes.readByte()[0]);
			print("TODO: modregrm for 0x83");

			opcode = Opcode(byte, reg);
			register = operand.RegisterOperand(getRegister(rm, rexPrefix));
			data = operand.ImmediateOperand(readImmediateSigned(bytes, 1));
			operands = [data, register];

		elif ((byte & top5BitsMask == opcodes.PUSH) or (byte & top5BitsMask == 0x58)):
			# push register
			# pop register
			rexPrefix.setDataSize(64);
			opcode, registerOperand = readRegBottomOpcodeBits(byte, rexPrefix);
			operands = [registerOperand];

		elif ((byte == 0x89) or (byte == 0x8b)):
			# 0x89 = mov r -> r/m
			# 0x8b = mov r/m -> r
			opcode = Opcode(byte);
			operands = decodeModRegRm(bytes, rexPrefix);

			if (byte == 0x8b):
				operands.reverse();

		elif (byte & top5BitsMask == 0xb8):
			# mov imm32 -> r32
			rexPrefix.setDataSize(32);
			opcode, registerOperand = readRegBottomOpcodeBits(byte, rexPrefix);
			operands = [operand.ImmediateOperand(readImmediate32Signed(bytes)), registerOperand];

		elif (byte == 0xc7):
			# mov imm32 -> rm32
			opcode = Opcode(byte);
			operands = decodeModRegRm(bytes, rexPrefix, readRmDisplacement = True, regIsOpcodeExtension = True);

		elif (byte == 0x63):
			# movsxd r64 -> r/m32 with rex.w
			print("TODO: movsxd/movslq 0x63 32/64 bit");
			opcode = Opcode(byte);
			operands = decodeModRegRm(bytes, rexPrefix);

		elif (byte == 0xe8):
			# call near rel16/32
			opcode = Opcode(byte);
			data = readImmediate32Signed(bytes);
			operands = [operand.ImmediateOperand(data)];

		elif (byte == 0xc3):
			# return near
			opcode = Opcode(byte);

		elif (byte == 0xc9):
			# leaveq
			opcode = Opcode(byte);

		else:
			print("\tRead unknown byte");
			print("\t\tLocation: \t" + getDisplayByteString(startByte));
			print("\t\tValue: \t\t" + getDisplayByteString(byte));
			break;


		if (opcode != None):
			instruction = Instruction(startByte, bytes.currentlyRead, opcode, operands);
			instructions.append(instruction);
		else:
			print("Opcode is None");
			break;


	return instructions;