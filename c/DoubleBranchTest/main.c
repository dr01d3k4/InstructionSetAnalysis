#include <stdio.h>
#include <stdlib.h>


void doBranch(int);


int main() {
	// int reached9 = 0;
	
	// for (int x = 0; x < 10; x += 1) {
		int x = 0;
		doBranch(x);

		// if ((x == 9) && !reached9) {
		// 	reached9 = 1;
		// 	x = 0;
		// }
	// }
	
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