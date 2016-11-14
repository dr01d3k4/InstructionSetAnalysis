from x86.x86 import x86;


architectures = {
	"x86": x86()
};


def getArchitecture(name):
	if (name in architectures):
		return architectures[name];
	else:
		print("Unknown architecture:", name);
		return None;