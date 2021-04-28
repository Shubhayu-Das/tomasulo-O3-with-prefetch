'''
MIT Licensed by Shubhayu Das, Veerendra S Devaraddi, Sai Manish Sasanapuri, copyright 2021

Developed for Processor Architecture course assignments 1 and 3 - Tomasulo Out-Of-Order Machine

This file contains some helper functions which are used in various places
'''


# Zero pad the binary numbers appropriately
def pad(number: str, n: int) -> str:
    number = number[2:]
    while len(number) < n:
        number = "0" + number
    return number

# Function to convert integers to binary - using 2's complement


def dec2bin(number: int, n_bits: int = 32) -> str:
    bin_number = '0'
    if(number < 0):
        bin_number = '1'
        number = 2**(n_bits-1)+number
    bin_number = bin_number + pad(bin(number), n_bits-1)
    return bin_number


# Function to convert binary to integer - using 2's complement
def bin2dec(number: str) -> int:
    no_bits = len(number)
    return -int(number[0])*2**(no_bits-1) + int(number[1:no_bits], 2)


if __name__ == "__main__":
    print(len(dec2bin(-10)), dec2bin(-10))
    print(len(dec2bin(10)), dec2bin(10))
