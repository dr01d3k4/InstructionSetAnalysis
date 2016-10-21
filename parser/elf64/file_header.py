from util.byte_util import bytesToHexString;


# https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h#L220
# https://uclibc.org/docs/elf-64-gen.pdf page 3
# #define EI_NIDENT	16
class Elf64Header(object):
	def __init__(self, e_ident, e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx):
		# unsigned char[EI_NIDENT] - elf indentification
		self._e_ident = e_ident; 
		# half - object file type
		self._e_type = e_type;
		# half - machine type
		self._e_machine = e_machine
		# word - object file version
		self._e_version = e_version;
		# addr - entry point address
		self._e_entry = e_entry;
		# off - program header offset
		self._e_phoff = e_phoff;
		# off - section header offset
		self._e_shoff = e_shoff;
		# word - processor-specific flags
		self._e_flags = e_flags;
		# half - elf header size
		self._e_ehsize = e_ehsize;
		# half - size of program header entry
		self._e_phentsize = e_phentsize;
		# half - number of program header entries
		self._e_phnum = e_phnum;
		# half - size of section header entry
		self._e_shentsize = e_shentsize;
		# half - number of section header entries
		self._e_shnum = e_shnum;
		# half - section name string table index
		self._e_shstrndx = e_shstrndx;

	@property
	def e_ident(self):
		return self._e_ident;
	@property
	def e_type(self):
		return self._e_type;			
	@property
	def e_machine(self):
		return self._e_machine;		
	@property
	def e_version(self):
		return self._e_version;		
	@property
	def e_entry(self):
		return self._e_entry;		
	@property
	def e_phoff(self):
		return self._e_phoff;		
	@property
	def e_shoff(self):
		return self._e_shoff;		
	@property
	def e_flags(self):
		return self._e_flags;		
	@property
	def e_ehsize(self):
		return self._e_ehsize;		
	@property
	def e_phentsize(self):
		return self._e_phentsize; 	
	@property
	def e_phnum(self):
		return self._e_phnum;		
	@property
	def e_shentsize(self):
		return self._e_shentsize; 	
	@property
	def e_shnum(self):
		return self._e_shnum;		
	@property
	def e_shstrndx(self):
		return self._e_shstrndx;

	def __repr__(self):
		itemSeparator = ",\n\t";
		return "Elf64Header(\n\t" \
			"e_ident = " + bytesToHexString(self._e_ident) + itemSeparator + \
			"e_type = " + bytesToHexString(self._e_type) + itemSeparator + \
			"e_machine = " + bytesToHexString(self._e_machine) + itemSeparator + \
			"e_version = " + bytesToHexString(self._e_version) + itemSeparator + \
			"e_entry = " + bytesToHexString(self._e_entry) + itemSeparator + \
			"e_phoff = " + bytesToHexString(self._e_phoff) + itemSeparator + \
			"e_shoff = " + bytesToHexString(self._e_shoff) + itemSeparator + \
			"e_flags = " + bytesToHexString(self._e_flags) +itemSeparator + \
			"e_ehsize = " + bytesToHexString(self._e_ehsize) + itemSeparator + \
			"e_phentsize = " + bytesToHexString(self._e_phentsize) + itemSeparator + \
			"e_phnum = " + bytesToHexString(self._e_phnum) + itemSeparator + \
			"e_shentsize = " + bytesToHexString(self._e_shentsize) + itemSeparator + \
			"e_shnum = " + bytesToHexString(self._e_shnum) + itemSeparator + \
			"e_shstrndx = " + bytesToHexString(self._e_shstrndx) + \
			"\n)";

	def __str__(self):
		return self.__repr__();
