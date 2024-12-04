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

    bits_value = int(bit_string, 2)

    return bits_value

def concatenateBytes(bytes_list):

    bit_string = ""
    for byte in bytes_list:
        bit_string += getBits(byte)

    bytes_value = convertBitStringToInt(bit_string)

    return bytes_value

if __name__ == "__main__":

    bytes_list = [1, 56, 126]

    print(concatenateBytes(bytes_list))

    print(chr(0))