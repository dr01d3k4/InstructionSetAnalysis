#include <stdio.h>
#include <stdlib.h>


void doBranch(int);


int main() {
	for (int x = 0; x < 10; x += 1) {
		doBranch(x);
	}
	
	return 0;
}


void doBranch(int x) {
	if (x < 5) {
		printf("x less than 5\n");
		for (int i = 0; i < 5; i += 1) {
			printf("On i: %d\n", i);
		}
		printf("Finished loop\n");
	} else {
		printf("x greater than or equal to 5\n");
		for (int i = 10; i > 5; i -= 1) {
			printf("On i: %d\n", i);
		}
		printf("Finished loop\n");
	}
}
