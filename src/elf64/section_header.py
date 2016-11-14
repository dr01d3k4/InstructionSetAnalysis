from util.byte_util import bytesToHexString;


# https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h#L315
# https://uclibc.org/docs/elf-64-gen.pdf page 8
class Elf64SectionHeader(object):
	def __init__(self, sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize):
		# word - section name
		self._sh_name = sh_name;
		# word - section type
		self._sh_type = sh_type;
		# xword - section attributes
		self._sh_flags = sh_flags;
		# addr - virtual address in memory
		self._sh_addr = sh_addr;
		# off - offset in file
		self._sh_offset = sh_offset;
		# xword - size of section
		self._sh_size = sh_size;
		# word - link to other section
		self._sh_link = sh_link;
		# word - miscellaneous information
		self._sh_info = sh_info;
		# xword - address alignment boundary
		self._sh_addralign = sh_addralign;
		# xword - size of entries, if section has table
		self._sh_entsize = sh_entsize;


	@property
	def sh_name(self):
		return self._sh_name;
	@property
	def sh_type(self):
		return self._sh_type;
	@property
	def sh_flags(self):
		return self._sh_flags;
	@property
	def sh_addr(self):
		return self._sh_addr;
	@property
	def sh_offset(self):
		return self._sh_offset;
	@property
	def sh_size(self):
		return self._sh_size;
	@property
	def sh_link(self):
		return self._sh_link;
	@property
	def sh_info(self):
		return self._sh_info;
	@property
	def sh_addralign(self):
		return self._sh_addralign;
	@property
	def sh_entsize(self):
		return self._sh_entsize;

	def __repr__(self):
		itemSeparator = ",\n\t";
		return "Elf64SectionHeader(\n\t" \
			"sh_name = " + bytesToHexString(self._sh_name) + itemSeparator + \
			"sh_type = " + bytesToHexString(self._sh_type) + itemSeparator + \
			"sh_flags = " + bytesToHexString(self._sh_flags) + itemSeparator + \
			"sh_addr = " + bytesToHexString(self._sh_addr) + itemSeparator + \
			"sh_offset = " + bytesToHexString(self._sh_offset) + itemSeparator + \
			"sh_size = " + bytesToHexString(self._sh_size) + itemSeparator + \
			"sh_link = " + bytesToHexString(self._sh_link) + itemSeparator + \
			"sh_info = " + bytesToHexString(self._sh_info) + itemSeparator + \
			"sh_addralign = " + bytesToHexString(self._sh_addralign) + itemSeparator + \
			"sh_entsize = " + bytesToHexString(self._sh_entsize) + \
			"\n)";

	def __str__(self):
		return self.__repr__();