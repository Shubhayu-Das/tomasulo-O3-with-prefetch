; Load first element and then add some number to it
; Then write it back to memory
; Repeat for 3 other elements in a supposed array

LW x2, 0(x0)
ADD x2, x2, x0
SW x2, 0(x0)
SUB x0, x0, x1