from util.string_util import reindent;


def dictToString(dictionary, name):
	s = ",\n\t";
	s += name;
	s += " = {";
	for key, value in dictionary.iteritems():
		s += "\n\t\t";
		s += "\"" + key + "\" = " + reindent(str(value), 2);
		s += ","
	s = s[:-1]; # Remove last '
	s += "\n\t}"
	return s;


class Elf64File(object):
	def __init__(self, fileHeader, sectionHeaders, sectionContents):
		self._fileHeader = fileHeader;
		self._sectionHeaders = sectionHeaders;
		self._sectionContents = sectionContents;

	@property
	def fileHeader(self):
		return self.fileHeader;

	@property
	def sectionHeaders(self):
		return self.sectionHeaders;

	@property
	def sectionContents(self):
		return self.sectionContents;


	def getSectionContents(self, sectionName):
		if (sectionName in self._sectionContents):
			return self._sectionContents[sectionName];
		else:
			return None;

	def setSectionContents(self, sectionName, value):
		if (sectionName in self._sectionContents):
			self._sectionContents[sectionName] = value;


	def __repr__(self):
		s = "Elf64File(\n";
		s += "\tfileHeader = " + reindent(str(self._fileHeader), 1);
		s += dictToString(self._sectionHeaders, "sectionHeaders");
		s += dictToString(self._sectionContents, "sectionContents");
		s += "\n)"
		
		return s;


	def __str__(self):
		return self.__repr__();