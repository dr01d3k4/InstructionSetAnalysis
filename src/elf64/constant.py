from util.byte_util import hexStringToInteger;


EI_NIDENT = 16
ELF_MAGIC_NUMBER_STRING = "\x7fELF"
ELF_MAGIC_NUMBER = hexStringToInteger(ELF_MAGIC_NUMBER_STRING);
EI_DATA = 5; # Endianness byte
ELFDATA2LSB = 1; # Little endian
ELFDATA2MSB = 2; # Big endian