OntCversion = '2.0.0'

'''
Zero Copy Source and Sink testing contract to help verify the function logic

Started: Nov 26th, 2019
Author: Yinghao Liu
'''

from ontology.interop.System.Runtime import Notify
from ontology.interop.System.Storage import Put, GetContext, Get, Delete
from ontology.builtins import concat
from ontology.interop.System.App import RegisterAppCall, DynamicAppCall
from ontology.libont import bytearray_reverse

def Main(operation, args):
    if operation == "setSinkSourceHash":
        sinkHash = args[0]
        sourceHash = args[1]
        return setSinkSourceHash(sinkHash, sourceHash)
    if operation == "testSink":
        Notify([args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], args[10]])
        return testSink(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], args[10])
    if operation == "testSource":
        return testSource(args[0])
    if operation == "testEqual":
        return testEqual(args[0])
    return False

def setSinkSourceHash(sinkHash, sourceHash):
    Put(GetContext(), "SINK", bytearray_reverse(sinkHash))
    Put(GetContext(), "SOURCE", bytearray_reverse(sourceHash))
    Notify(["set", sinkHash, sourceHash])
    return True

def testSink(bl, u8, u16, u32, u64, b, bs, vbs, addr, hash1, str1):
    sinkHash = Get(GetContext(), "SINK")
    Notify(["sinkHash", sinkHash])
    buff = None
    buff = DynamicAppCall(sinkHash, "WriteBool", [bl, buff])
    Notify([1, buff])

    buff = DynamicAppCall(sinkHash, "WriteUint8", [u8, buff])
    Notify([2, buff])

    buff = DynamicAppCall(sinkHash, "WriteUint16", [u16, buff])
    Notify([3, buff, 0xFFFF, 0xFFFF>0])

    buff = DynamicAppCall(sinkHash, "WriteUint32", [u32, buff])
    Notify([4, buff])


    buff = DynamicAppCall(sinkHash, "WriteUint64", [u64, buff])
    Notify([5, buff, u64, 18446744073709551615])

    buff = DynamicAppCall(sinkHash, "WriteByte", [b, buff])
    Notify([6, buff])

    buff = DynamicAppCall(sinkHash, "WriteBytes", [bs, buff])
    Notify([7, buff])

    buff = DynamicAppCall(sinkHash, "WriteVarBytes", [vbs, buff])
    Notify([8, buff])

    buff = DynamicAppCall(sinkHash, "WriteBytes20", [addr, buff])
    Notify([9, buff])

    buff = DynamicAppCall(sinkHash, "WriteBytes32", [hash1, buff])
    Notify([10, buff])

    buff = DynamicAppCall(sinkHash, "WriteString", [str1, buff])
    Notify([11, buff])

    return buff



def testEqual(v):
    v1V = concat(v[0:1], b'\x00')
    Notify(["222",v1V, v1V>0x80, v1V == 0x80])
    Notify(["333", v1V > b'\x80\x00', v1V == b'\x80\x00'])
    Notify(["444", v[0:1] == b'\xfe', concat(v[0:1], b'\x00') == 0xfe])

def testSource(buff):
    sourceHash = Get(GetContext(), "SOURCE")
    Notify(["sourceHash", sourceHash])
    offset = 0
    res = DynamicAppCall(sourceHash, "NextBool", [buff, offset])
    Notify([1, res, False])

    res = DynamicAppCall(sourceHash, "NextUint8", [buff, res[1]])
    Notify([2, res, 255])

    res = DynamicAppCall(sourceHash, "NextUint16", [buff, res[1]])
    Notify([3, res, 65535])

    res = DynamicAppCall(sourceHash, "NextUint32", [buff, res[1]])
    Notify([4, res, 4294967295])

    res = DynamicAppCall(sourceHash, "NextUint64", [buff, res[1]])
    Notify([5, res, 10100])

    res = DynamicAppCall(sourceHash, "NextByte", [buff, res[1]])
    Notify([6, res, 200])

    res = DynamicAppCall(sourceHash, "NextBytes", [buff, res[1], 6])
    Notify([7, res, "hahaha"])

    res = DynamicAppCall(sourceHash, "NextVarBytes", [buff, res[1]])
    Notify([8, res, "heiheihei"])

    res = DynamicAppCall(sourceHash, "NextBytes20", [buff, res[1]])
    Notify([9, res])

    res = DynamicAppCall(sourceHash, "NextBytes32", [buff, res[1]])
    Notify([10, res])

    res = DynamicAppCall(sourceHash, "NextString", [buff, res[1]])
    Notify([11, res])

    return buff
