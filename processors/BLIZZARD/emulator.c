#include "stdbool.h"
#include "stdint.h"
#include "stdio.h"

typedef bool status;
typedef int64_t sW;
typedef uint64_t uW;

status increment_data_pointer(void);
status decrement_data_pointer(void);

#define limit 10

sW flash[128] = {4, 0, 4, 2, 4, 1, 5};
sW memory[128];

sW data_stack[limit];

uW data_pointer;

uW program_counter;

sW top() {
	if (data_pointer == 0) {
		return data_stack[limit - 1];
	}
	return data_stack[data_pointer - 1];
}

sW pop() {
	sW value = top();
	decrement_data_pointer();
	return value;
}

status push(sW value) {
	data_stack[data_pointer] = value;
	increment_data_pointer();
	return 0;
}

status increment_data_pointer() {
	if (data_pointer == limit - 1) {
		data_pointer = 0;
		return 0;
	}
	data_pointer ++;
	return 0;
}

status decrement_data_pointer() {
	if (data_pointer == 0) {
		data_pointer = limit - 1;
		return 0;
	}
	data_pointer --;
	return 0;
}

status clock() {
	sW opcode = flash[program_counter];
	switch (opcode) {
		case 1:
			push(pop() + pop());
			break;
		case 2: // CAN BE REMOVED (Just do "0 1 JL", which evaluates to false, but removes that item anyways)
			pop();
			break;
		case 3:
			push(~(pop() | pop()));
			break;
		case 4:
			push(flash[program_counter + 1]);
			program_counter += 1;
			break;
		case 5:
			if (pop() < pop()) {
				program_counter = pop();
				return 0;
			} else {
				pop();
			}
			break;
		case 6:
			push(memory[pop()]);
			break;
		case 7:
			memory[pop()] = pop();
			break;
		case 8:
			push(top());
			break;
		case 9:
			sW v1 = pop();
			sW v2 = pop();
			push(v1);
			push(v2);
			break;
		case 10:
			push(program_counter);
			break;
		default:
			return 1;
	}
	program_counter += 1;
	return 0;
}

status main() {
	while (1) {
		status code = clock();
		if (code) {
			break;
		}
	}
	printf("%lld", top());
	return 0;
}