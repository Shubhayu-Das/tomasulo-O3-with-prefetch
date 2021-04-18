LW x1, 0(x2)
ADD x2, x1, x1
BNE x1, x2, EXIT
SUB x3, x5, x1

; This is to test the branch instruction
EXIT:
SW x2, 10(x1)