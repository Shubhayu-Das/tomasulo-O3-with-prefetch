# Zero pad the binary numbers appropriately
def pad(number, n):
    number = number[2:]
    while len(number) < n:
        number = "0" + number

    return number

# Function to convert integers to binary - using 2's complement


def dec2bin(number, n_bits=32):
    if(number & (1 << (n_bits - 1))) != 0:
        number = number - (1 << n_bits)

    formatter = "{" + f"0:0{n_bits}b" + "}"

    return formatter.format(number).replace('-', '')

# Function to convert binary to integer - using 2's complement


def bin2dec(number):
    no_bits = len(number)
    return -int(number[0])*2**(no_bits-1) + int(number[1:no_bits],2)


if __name__ == "__main__":
    print(len(dec2bin(-10)), dec2bin(-10))
    print(len(dec2bin(10)), dec2bin(10))
