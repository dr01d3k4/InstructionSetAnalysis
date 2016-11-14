from gcc import gcc;


compilers = {
	"gcc": gcc()
};


def getCompiler(name):
	if (name in compilers):
		return compilers[name];
	else:
		print("Unknown compiler:", name);
		return None;