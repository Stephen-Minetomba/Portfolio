section .text
    global _start

_start:
    ; I can't believe this actually works
    intArray8 msg, 5 ; int msg[5]
    setAtIndexI msg, 0, "w", 8 ; msg[0] = "w"
    setAtIndexI msg, 1, "s", 8 ; msg[1] = "s"
    setAtIndexI msg, 2, "p", 8 ; msg[2] = "p"

    int8 x ; int x
    int8 y ; int y

    seti8 y, 35 ; y = 35
    setr8 x, y ; x = y
    
    print x, 1 ; write(1, &x, 1)
    print y, 1 ; write(1, &y, 1)
    newline ; write(1, &newline_char, 1)
    
    print msg, 5 ; write(1, &msg, 5)
    
    exit 0 ; exit(0)