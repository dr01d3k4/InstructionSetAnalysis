# https://uclibc.org/docs/elf-64-gen.pdf page 9
class Elf64Symbol(object):
	def __init__(self):
		# word - symbol name
		self._st_name = st_name;
		# unsigned char - type and binding attributes
		self._st_info = st_info;
		# unsigned char - reserved
		self._st_other = st_other;
		# half - section table index
		self._st_shndx = st_shndx;
		# addr - symbol value
		self._st_value = st_value;
		# xword - size of object
		self._st_size = st_size;


# https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h#L254
# https://uclibc.org/docs/elf-64-gen.pdf page 12
class Elf64ProgramHeader(object):
	def __init__(self, p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align):
		# word - type of segment
		self._p_type = p_type;
		#  word - segment attributes
		self._p_flags = p_flags;
		# off - offset in file
		self._p_offset = p_offset;
		# addr - virtual address in memory
		self._p_vaddr = p_vaddr;
		# addr - reserved
		self._p_paddr = p_paddr;
		# xword - size of segment in file
		self._p_filesz = p_filesz;
		# xword - size of segment in memory
		self._p_memsz = p_memsz;
		# xword - alignment of segment
		self._p_align = p_align;