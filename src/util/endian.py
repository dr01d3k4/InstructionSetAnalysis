LITTLE = 0;
BIG = 1;


def toString(endianness):
	if (endianness == LITTLE):
		return "LITTLE";
	elif (endianness == BIG):
		return "BIG";
	else:
		return "None";