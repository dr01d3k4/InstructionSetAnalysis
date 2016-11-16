from gcc import gcc;
from ghc import ghc;
from clang import clang;


compilers = {
	"gcc": gcc(),
	"ghc": ghc(),
	"clang": clang()
};


def getCompiler(name):
	if (name in compilers):
		return compilers[name];
	else:
		print("Unknown compiler:", name);
		return None;