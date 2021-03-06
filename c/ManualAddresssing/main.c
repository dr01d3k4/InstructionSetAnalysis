#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>


struct Test {
	int32_t a;
	int32_t b;
};


int main() {
	const int TEST_ARRAY_LENGTH = 100;
	struct Test* testArray;

	testArray = (struct Test*) calloc(TEST_ARRAY_LENGTH, sizeof(struct Test));


	// [reg + reg*scale + imm]
	// [testArray + i<<3 + 4]
	// printf("testArray location: %p\n", (void*) testArray);

	// i is stored in [rbp - 0x10]
	for (int i = 0; i < TEST_ARRAY_LENGTH; i++) {
		testArray[i].b = 5;
		// *(((char*) &testArray[i]) + 4) = 5;


		__asm__ __volatile__ (
			""
		);
	}

	free(testArray);

	return 0;
}
