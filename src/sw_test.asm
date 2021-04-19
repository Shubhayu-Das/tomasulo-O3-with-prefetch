; ADD x2, x2, x3
LW x1, 0(x2)
ADD x4, x1, x1
; SUB x4, x3, x2
SW x2, 0(x1)
SW x3, 0(x4)
ADD x1, x1, x2
LW x2, 0(x1)