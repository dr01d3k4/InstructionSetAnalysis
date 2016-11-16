#include <iostream>

int add(int, int);


int main() {
	std::cout << "Hello world!\n";

	int x = 5;
	int y = 7;
	int z = add(x, y);

	std::cout << z << "\n";

	return 0;
}


int add(int a, int b) {
	return a + b;
}


