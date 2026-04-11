#include "stdint.h"
#include "stdbool.h"

typedef bool status;
typedef uint64_t uW;
typedef int64_t sW;

sW accumulator;
uW program_counter;
sW memory[128];
sW argument;

sW read(uW address, sW* interface) {
	return interface[address];
}

void write(uW address, sW value, sW* interface) {
	interface[address] = value;
	return;
}

void alu(status op) {
	if (op) {
		accumulator = accumulator << 1;
	} else {
		accumulator = ~(accumulator | argument);
	}
	return;
}

status clock() {
	increment_pc(&program_counter);
	sW opcode = read(program_counter, &memory);
	sW opargument = read(program_counter + 1, &memory);
	switch (opcode) {
		case 1: // LAR/Load argument register/Load into argument register
			argument = opargument;
			program_counter ++;
			break;
		case 2: // NOR/Not or
			alu(0);
			break;
		case 3: // STR/Store
			write(argument, accumulator, &memory);
			break;
		case 4: // JLZ/Jump less zero/Jump if less than zero
			if (accumulator < 0)
				program_counter = argument;
			break;
		case 5: // PC/Program counter/Put program counter into argument
			argument = program_counter;
			break;
		case 6: // RES/Resolve/Resolve argument to memory cell value
			argument = read(argument, &memory);
			break;
		default: // Any other instruction shuts down the CPU
			return 1;
	}
	return 0;
}

#include "stdio.h"
status main() {
	while (1) {
		status code = clock();
		if (code) {
			break;
		}
	}
	printf("%d", accumulator);
	return 0;
}