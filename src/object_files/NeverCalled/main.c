#include <stdio.h>
#include <stdlib.h>


void neverCalled();


int main() {
	for (int i = 0; i < 20; i += 1) {
		neverCalled();
	}
}


void neverCalled() {
	int x = 0;
	int j = 0;

	for (int i = 0; i < 10; i += 1) {
		if (x == 0) {
			j += 1;
			// neverCalled();
		} else {
			j += 1;
			// neverCalled();
		}
	}
}	