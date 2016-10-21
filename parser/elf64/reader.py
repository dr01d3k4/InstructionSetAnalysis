from __future__ import print_function;
from elf64_file import Elf64File;
from file_header import Elf64Header;
from section_header import Elf64SectionHeader;
from util.byte_util import hexStringToInteger, collapseBytesToInteger, readNullTerminatedString, bytesToHexString, bytesToAsciiCharString;
from util.binary_file import BinaryFile;
import util.endian as endian;
import constant;


"""
https://0xax.gitbooks.io/linux-insides/content/Theory/ELF.html

https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h

https://uclibc.org/docs/elf-64-gen.pdf
"""

# https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h#L14
# https://uclibc.org/docs/elf-64-gen.pdf page 2
# /* 64-bit ELF base types. */
# typedef __u64	Elf64_Addr;	// 8 (unsigned program address)
# typedef __u16	Elf64_Half;	// 2 (unsigned medium integer)
# typedef __s16	Elf64_SHalf;	// ? (2 signed medium integer?)
# typedef __u64	Elf64_Off;	// 8
# typedef __s32	Elf64_Sword;	// 4 (signed integer)
# typedef __u32	Elf64_Word;	// 4 (unsigned integer)
# typedef __u64	Elf64_Xword;	// 8 (unsigned long integer)
# typedef __s64	Elf64_Sxword;	// 8 (signed long integer)


def runEndiannessTest(f):
	print("Running endianness test");
	print("16 x 1 byte:");
	f.seek(0);
	f.endianness = endian.BIG;
	print("Big\t", bytesToHexString(f.readCharArray(16)));
	f.seek(0);
	f.endianness = endian.LITTLE;
	print("Little\t", bytesToHexString(f.readCharArray(16)));

	print("");
	print("8 x 2 bytes:");
	f.seek(0);
	f.endianness = endian.BIG;
	print("Big\t", bytesToHexString(f.readArray(2, 8)));
	f.seek(0);
	f.endianness = endian.LITTLE;
	print("Little\t", bytesToHexString(f.readArray(2, 8)));

	print("");
	print("4 x 4 bytes:");
	f.seek(0);
	f.endianness = endian.BIG;
	print("Big\t", bytesToHexString(f.readArray(4, 4)));
	f.seek(0);
	f.endianness = endian.LITTLE;
	print("Little\t", bytesToHexString(f.readArray(4, 4)))


"""
Checks the magic number in the e_ident value. Returns true if it matches, else false.
"""
def checkMagicNumber(e_ident):
	return (constant.ELF_MAGIC_NUMBER == collapseBytesToInteger(e_ident[:len(constant.ELF_MAGIC_NUMBER_STRING)]));


"""
Gets the endianness from the e_ident. If endianness is invalid, prints to output and returns big endian.
"""
def getEndianness(e_ident):
	endiannessByte = e_ident[constant.EI_DATA];
	if (endiannessByte == constant.ELFDATA2LSB):
		return endian.LITTLE;
	elif (endiannessByte == constant.ELFDATA2MSB):
		return endian.BIG;
	else:
		print("Endianness value not recognised: " + str(endiannessByte));
		return endian.BIG;


"""
Reads the ELFF64 header from a binary file.
Changes endianness in the file object.
If header invalid (e.g. incorrect magic number), returns None and the error message, else returns header and empty string.
"""
def readElf64Header(f):
	f.endianness = endian.BIG;
	e_ident = f.readCharArray(constant.EI_NIDENT);
	
	if (not checkMagicNumber(e_ident)):
		return None, "Wrong file type";

	f.endianness = getEndianness(e_ident);

	e_type = f.readHalf();
	e_machine = f.readHalf(); # x86-64 = 0x003e
	e_version = f.readWord();
	e_entry = f.readAddr();
	e_phoff = f.readOff();
	e_shoff = f.readOff();
	e_flags = f.readWord();
	e_ehsize = f.readHalf();
	e_phentsize = f.readHalf();
	e_phnum = f.readHalf();
	e_shentsize = f.readHalf();
	e_shnum = f.readHalf();
	e_shstrndx = f.readHalf();

	return Elf64Header(e_ident, e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx), "";


"""
Reads the ELFF64 section header from a binary file.
"""
def readElf64SectionHeader(f):
	sh_name = f.readWord();
	sh_type = f.readWord();
	sh_flags = f.readXword();
	sh_addr = f.readAddr();
	sh_offset = f.readOff();
	sh_size = f.readXword();
	sh_link = f.readWord();
	sh_info = f.readWord();
	sh_addralign = f.readXword();
	sh_entsize = f.readXword();

	sectionHeader = Elf64SectionHeader(sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize);

	return sectionHeader;


"""
Reads and returns an array of section headers from a binary file.
File header passed in is to get offset, size and count for section headers.
"""
def readElf64SectionHeaders(f, elf64Header):
	sectionHeaders = [ ];

	# Offset to start of section header table
	e_shoff = collapseBytesToInteger(elf64Header.e_shoff);
	# Number of section headers
	e_shnum = collapseBytesToInteger(elf64Header.e_shnum);
	# Size of section headers
	e_shentsize = collapseBytesToInteger(elf64Header.e_shentsize);

	for i in xrange(0, e_shnum):
		f.seek(e_shoff + (i * e_shentsize));
		sectionHeader = readElf64SectionHeader(f);
		sectionHeaders.append(sectionHeader);

	return sectionHeaders;


def readSectionNameStringTable(f, elf64Header, sectionHeaders):
	# Section name string table index
	e_shstrndx = collapseBytesToInteger(elf64Header.e_shstrndx);
	sectionNameStringTableHeader = sectionHeaders[e_shstrndx];

	sectionNameOffset = collapseBytesToInteger(sectionNameStringTableHeader.sh_offset);
	sectionNameSize = collapseBytesToInteger(sectionNameStringTableHeader.sh_size);

	f.seek(sectionNameOffset);
	sectionNames = f.readCharArray(sectionNameSize);

	return sectionNames;


def createSectionHeadersDict(sectionHeaders, sectionNames):
	sectionHeadersDict = { };

	for sectionHeader in sectionHeaders:
		sh_name = collapseBytesToInteger(sectionHeader.sh_name);
		name = readNullTerminatedString(sectionNames, sh_name);
		sectionHeadersDict[name] = sectionHeader;

	return sectionHeadersDict;


def readSectionContents(f, sectionHeader):
	offset = collapseBytesToInteger(sectionHeader.sh_offset);
	size = collapseBytesToInteger(sectionHeader.sh_size);
	f.seek(offset);
	contents = f.readCharArray(size);
	return contents;


"""
Reads an ELF64 file from the filename.
If file is invalid, returns None and error message.
"""
def readElf64File(filename):
	elf64File = None;
	errorMessage = "";

	while (True):
		with BinaryFile(filename) as f:
			# runEndiannessTest(f);
			# print("");

			f.seek(0);
			elf64Header, errorMessage = readElf64Header(f);
			if (elf64Header == None):
				break;

			sectionHeaders = readElf64SectionHeaders(f, elf64Header);

			sectionNames = readSectionNameStringTable(f, elf64Header, sectionHeaders);

			sectionHeadersDict = createSectionHeadersDict(sectionHeaders, sectionNames);

			sectionContents = {name: readSectionContents(f, header) for name, header in sectionHeadersDict.iteritems()};

			elf64File = Elf64File(elf64Header, sectionHeadersDict, sectionContents);
		break;

	return elf64File, errorMessage;