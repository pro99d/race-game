from random import randint as ra
def r():
    return bool(ra(0, 1))
def to_bytes(num, bool1, bool2, bool3, bool4):
    """
    format:
    \000\num(1-4)\0\bool4\0\bool3\0\bool2\0\bool1
    :param integer:
    :param forward:
    :param backward:
    :param left:
    :param right:
    :return:
    """
    #print(bin(num))
    num = num<<4
    bool1 = int(bool1)
    bool2 = int(bool2)<<1
    bool3 = int(bool3)<<2
    bool4 = int(bool4)<<3
    num = num+bool1+bool2+bool3+bool4
    return bytes([num])

def from_bytes(data):
    data = int(ord(data))
    data = bin(data)[2:]
    data = "0"*(7-len(data))+data
    num = int(data[:3], 2)
    data = data[3:]
    bools = []
    data = data[::-1]
    for i in range(4):
        bools.append(bool(int(data[i])))
    b1, b2, b3, b4 = bools
    return num, b1, b2, b3, b4
def decode_server(data):
    players = []
    print(data)
    res = []
    for i in data:
        res.append(from_bytes(chr(i)))

def test(players):
    playern = []
    for i in range(players):
        num = i+1
        b1=r()
        b2=r()
        b3=r()
        b4=r()
        byte = str(to_bytes(num, b1, b2, b3, b4))[2:-1]
        if i==0:
            byte = chr(int(byte[2:], 16))
        playern.append(byte)
    res = str.encode("".join(playern))
    return res

if __name__=="__main__":
    res = test(4)
    decode_server(res)
