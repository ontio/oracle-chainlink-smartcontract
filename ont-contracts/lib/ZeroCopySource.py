OntCversion = '2.0.0'

'''
Zero Copy Source contract to help deserialize data or struct from a series of bytes 

Started: Nov 26th, 2019
Author: Yinghao Liu
'''

from ontology.interop.System.Runtime import Notify
from ontology.libont import str
from ontology.builtins import concat

'''
If the returned offset is -1, means the offset is out of the buff's range
'''


def Main(operation, args):
    if operation == "NextBool":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextBool(buff, offset)
    if operation == "NextByte":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextByte(buff, offset)
    if operation == "NextUint8":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextUint8(buff, offset)
    if operation == "NextUint16":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextUint16(buff, offset)
    if operation == "NextUint32":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextUint32(buff, offset)
    if operation == "NextUint64":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextUint64(buff, offset)
    if operation == "NextUint255":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextUint255(buff, offset)
    if operation == "NextBytes":
        assert (len(args) == 3)
        buff = args[0]
        offset = args[1]
        count = args[2]
        return NextBytes(buff, offset, count)
    if operation == "NextVarUint":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextVarUint(buff, offset)
    if operation == "NextVarBytes":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextVarBytes(buff, offset)
    if operation == "NextBytes20":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextBytes20(buff, offset)
    if operation == "NextBytes32":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextBytes32(buff, offset)
    if operation == "NextString":
        assert (len(args) == 2)
        buff = args[0]
        offset = args[1]
        return NextString(buff, offset)
    return False


def NextBool(buff, offset):
    if offset + 1 > len(buff):
        return [False, -1]
    val = buff[offset:offset + 1]
    if val == 1:
        return [True, offset + 1]
    elif val == 0:
        return [False, offset + 1]
    assert (False)


def NextByte(buff, offset):
    if offset + 1 > len(buff):
        return [0, -1]
    return [buff[offset:offset + 1], offset + 1]


def NextUint8(buff, offset):
    if offset + 1 > len(buff):
        return [0, -1]
    return [_convertBytesToNum(buff[offset:offset + 1]), offset + 1]


def NextUint16(buff, offset):
    if offset + 2 > len(buff):
        return [0, -1]
    return [_convertBytesToNum(buff[offset:offset + 2]), offset + 2]


def NextUint32(buff, offset):
    if offset + 4 > len(buff):
        return [0, -1]
    return [_convertBytesToNum(buff[offset:offset + 4]), offset + 4]


def NextUint64(buff, offset):
    if offset + 8 > len(buff):
        return [0, -1]
    res = _convertBytesToNum(buff[offset:offset + 8])
    return [res, offset + 8]


def NextUint255(buff, offset):
    if offset + 32 > len(buff):
        return [0, -1]
    # TODO, limit the converted bytes has the maximum length of 32
    return [_convertBytesToNum(buff[offset:offset + 32]), offset + 32]


def NextBytes(buff, offset, count):
    if offset + count > len(buff):
        return [0, -1]
    return [buff[offset:offset + count], offset + count]


def NextVarUint(buff, offset):
    res = NextByte(buff, offset)
    fb = res[0]
    offset = res[1]
    assert (res[1] > 0)
    # we can also use if concat(fb, b'\x00') == 0xfd:
    if fb == b'\xfd':
        return NextUint16(buff, offset)
    elif fb == b'\xfe':
        return NextUint32(buff, offset)
    elif fb == b'\xff':
        return NextUint64(buff, offset)
    else:
        return [fb, offset]


def NextVarBytes(buff, offset):
    res = NextVarUint(buff, offset)
    return NextBytes(buff, res[1], res[0])


def NextBytes20(buff, offset):
    if offset + 20 > len(buff):
        return [0, -1]
    return [buff[offset:offset + 20], offset + 20]

def NextBytes32(buff, offset):
    if offset + 32 > len(buff):
        return [0, -1]
    return [buff[offset:offset + 32], offset + 32]

def NextString(buff, offset):
    return NextVarBytes(buff, offset)




def _convertBytesToNum(_bs):
    firstNonZeroPostFromR2L = _getFirstNonZeroPosFromR2L(_bs)
    assert (firstNonZeroPostFromR2L >= 0)
    Notify(["111", _bs, firstNonZeroPostFromR2L])
    if firstNonZeroPostFromR2L > len(_bs):
        return concat(_bs, b'\x00')
    else:
        return _bs[:firstNonZeroPostFromR2L]


def _getFirstNonZeroPosFromR2L(_bs):
    bytesLen = len(_bs)
    for i in range(bytesLen):
        byteI = _bs[bytesLen - i - 1:bytesLen - i]
        if byteI != b'\x00':
            # convert byte to int
            byteI = concat(byteI, b'\x00')
            if byteI >= 0x80:
                return bytesLen + 1 - i
            else:
                return bytesLen - i
    return -1