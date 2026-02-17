// A
input(1)
// B
input(2)
// C
input(3)
// Full adder truth table implementation in BitLang
if (1, 0) {
    if (2, 0) {
        if (3, 1) {
            toggle(4)
        }cif(3, 1)
    }cif(2, 0)
}cif(1, 0)
if (1, 0) {
    if (2, 1) {
        if (3, 0) {
            toggle(4)
        }cif(3, 0)
    }cif(2, 1)
}cif(1, 0)
if (1, 0) {
    if (2, 1) {
        if (3, 1) {
            toggle(5)
        }cif(3, 1)
    }cif(2, 1)
}cif(1, 0)
if (1, 1) {
    if (2, 0) {
        if (3, 0) {
            toggle(4)
        }cif(3, 0)
    }cif(2, 0)
}cif(1, 1)
if (1, 1) {
    if (2, 0) {
        if (3, 1) {
            toggle(5)
        }cif(3, 1)
    }cif(2, 0)
}cif(1, 1)
if (1, 1) {
    if (2, 1) {
        if (3, 0) {
            toggle(5)
        }cif(3, 0)
    }cif(2,1)
}cif(1, 1)
if (1, 1) {
    if (2, 1) {
        if (3, 1) {
            toggle(4)
            toggle(5)
        }cif(3, 1)
    }cif(2, 1)
}cif(1, 1)
// Sum
print(4)
// Carry out
print(5)
