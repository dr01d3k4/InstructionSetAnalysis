#include <stdio.h>
#include <stdlib.h>


int add(int, int);


int main() {
	printf("Hello world!\n");

	int x = 5;
	int y = 7;
	int z = add(x, y);
	printf("%d\n", z);

	return 0;
}


int add(int a, int b) {
	return a + b;
}


