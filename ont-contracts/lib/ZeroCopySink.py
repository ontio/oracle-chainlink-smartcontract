OntCversion = '2.0.0'

'''
Zero Copy Source contract to help serialize data or struct to a series of bytes 

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
    if operation == "WriteBool":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteBool(v, buff)
    if operation == "WriteByte":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteByte(v, buff)
    if operation == "WriteUint8":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteUint8(v, buff)
    if operation == "WriteUint16":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteUint16(v, buff)
    if operation == "WriteUint32":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteUint32(v, buff)
    if operation == "WriteUint64":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteUint64(v, buff)
    if operation == "WriteUint255":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteUint255(v, buff)
    if operation == "WriteVarBytes":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteVarBytes(v, buff)
    if operation == "WriteBytes20":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteBytes20(v, buff)
    if operation == "WriteBytes32":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteBytes32(v, buff)
    if operation == "WriteString":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteString(v, buff)
    if operation == "WriteBytes":
        assert (len(args) == 2)
        v = args[0]
        buff = args[1]
        return WriteBytes(v, buff)
    return False


def WriteBool(v, buff):
    if v == True:
        buff = concat(buff, b'\x01')
    elif v == False:
        buff = concat(buff, b'\x00')
    else:
        assert (False)
    return buff

def WriteByte(v, buff):
    assert (len(v) == 1)
    vBs = v[0:1]
    buff = concat(buff, vBs)
    return buff


def WriteUint8(v, buff):
    assert (v >= 0 and v <= 0xFF)
    buff = concat(buff, _convertNumToBytes(v, 1))
    return buff


def WriteUint16(v, buff):
    assert (v >= 0 and v <= 0xFFFF)
    buff = concat(buff, _convertNumToBytes(v, 2))
    return buff


def WriteUint32(v, buff):
    assert (v >= 0 and v <= 0xFFFFFFFF)
    buff = concat(buff, _convertNumToBytes(v, 4))
    return buff


def WriteUint64(v, buff):
    assert (v >= 0 and v <= 0xFFFFFFFFFFFFFFFF)
    buff = concat(buff, _convertNumToBytes(v, 8))
    return buff


def WriteUint255(v, buff):
    assert (v >= 0 and v <= 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff)
    return WriteBytes(_convertNumToBytes(v, 32), buff)


def WriteBytes(v, buff):
    return concat(buff, v)


def WriteVarBytes(v, buff):
    return WriteBytes(v, buff)

def WriteBytes20(v, buff):
    assert (len(v) == 20)
    return WriteBytes(v, buff)

def WriteBytes32(v, buff):
    assert (len(v) == 32)
    return WriteBytes(v, buff)

def WriteString(v, buff):
    return WriteVarBytes(v, buff)


def _convertNumToBytes(_val, bytesLen):
    l = len(_val)
    if l < bytesLen:
        for i in range(bytesLen - l):
            _val = concat(_val, b'\x00')
    if l > bytesLen:
        _val = _val[:bytesLen]
    return _val

