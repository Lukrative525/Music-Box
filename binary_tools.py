def reverseBits(bit_string):

    return bit_string[::-1]

def padBitsWithZeros(bit_string):

    while len(bit_string) < 8:
        bit_string += "0"

    return bit_string

def removeBinaryIdentifier(bit_string):

    for i in range(len(bit_string)):
        if bit_string[i] == "b":
            bit_string = bit_string[i + 1:]
            break

    return bit_string

def getBits(byte_as_int):

    bit_string = bin(byte_as_int)
    bit_string = removeBinaryIdentifier(bit_string)
    bit_string = reverseBits(bit_string)
    bit_string = padBitsWithZeros(bit_string)
    bit_string = reverseBits(bit_string)

    return bit_string

def convertBitStringToInt(bit_string):

    bit_int = int(bit_string, 2)

    return bit_int

if __name__ == "__main__":

    test_int = 130
    bit_string = getBits(test_int)
    print(convertBitStringToInt(bit_string))