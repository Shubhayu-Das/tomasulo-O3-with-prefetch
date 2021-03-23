; This is taken from Week5b class slides

; I am decreasing the offset, since my entry contains only 64 rows for now
LW x6, 12(x2)
LW x2, 45(x3)

MUL x0, x2, x4
SUB x8, x6, x2
; I am changing x10 to x5 in the next instruction, because I only have x0 to x9
DIV x5, x0, x6
ADD x6, x8, x2