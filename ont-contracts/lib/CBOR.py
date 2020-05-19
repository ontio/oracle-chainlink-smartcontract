############## COBR Library############
# ec8a6c55b34a6d3488db02742ad199eda4fd72c1
from ontology.interop.System.App import RegisterAppCall

MAJOR_TYPE_INT = 0
MAJOR_TYPE_NEGATIVE_INT = 1
MAJOR_TYPE_BYTES = 2
MAJOR_TYPE_STRING = 3
MAJOR_TYPE_ARRAY = 4
MAJOR_TYPE_MAP = 5
MAJOR_TYPE_CONTENT_FREE = 7

BufferCall = RegisterAppCall('d5f12664535717af51f52fe2aa88a18d327ea1b9', 'operation', 'args')

def Main(operation, args):
    if operation == 'encodeType':
        assert (len(args) == 3)
        buf = args[0]
        major = args[1]
        value = args[2]
        return encodeType(buf, major, value)

    if operation == 'encodeIndefiniteLengthType':
        assert (len(args) == 2)
        buf = args[0]
        major = args[1]
        return encodeIndefiniteLengthType(buf, major)

    if operation == 'encodeUInt':
        assert (len(args) == 2)
        buf = args[0]
        value = args[1]
        return encodeUInt(buf, value)

    if operation == 'encodeInt':
        assert (len(args) == 2)
        buf = args[0]
        value = args[1]
        return encodeInt(buf, value)

    if operation == 'encodeBytes':
        assert (len(args) == 2)
        buf = args[0]
        value = args[1]
        return encodeBytes(buf, value)

    if operation == 'encodeString':
        assert (len(args) == 2)
        buf = args[0]
        value = args[1]
        return encodeString(buf, value)

    if operation == 'startArray':
        assert (len(args) == 1)
        buf = args[0]
        return startArray(buf)

    if operation == 'startMap':
        assert (len(args) == 1)
        buf = args[0]
        return startMap(buf)

    if operation == 'endSequence':
        assert (len(args) == 1)
        buf = args[0]
        return endSequence(buf)
    return True

def encodeType(buf, major, value):
    if value <= 23:
        buf = BufferCall('WriteUint8', [(major << 5) | value, buf])
    elif value <= 0xFF:
        buf = BufferCall('WriteUint8', [(major << 5) | 24, buf])
        buf = BufferCall('WriteUint8', [value, buf])
    elif value <= 0xFFFF:
        buf = BufferCall('WriteUint8', [(major << 5) | 25, buf])
        buf = BufferCall('WriteUint16', [value, buf])
    elif value <= 0xFFFFFFFF:
        buf = BufferCall('WriteUint8', [(major << 5) | 26, buf])
        buf = BufferCall('WriteUint32', [value, buf])
    elif value <= 0xFFFFFFFFFFFFFFFF:
        buf = BufferCall('WriteUint8', [(major << 5) | 27, buf])
        buf = BufferCall('WriteUint64', [value, buf])
    return buf


def encodeIndefiniteLengthType(buf, major):
    return BufferCall('WriteUint8', [(major << 5 | 31), buf])


def encodeUInt(buf, value):
    return encodeType(buf, MAJOR_TYPE_INT, value)


def encodeInt(buf, value):
    if value >= 0:
        return encodeType(buf, MAJOR_TYPE_INT, value)
    else:
        return encodeType(buf, MAJOR_TYPE_NEGATIVE_INT, -1 - value)


def encodeBytes(buf, value):
    buf = encodeType(buf, MAJOR_TYPE_BYTES, len(value))
    return BufferCall('WriteBytes', [value, buf])


def encodeString(buf, value):
    buf = encodeType(buf, MAJOR_TYPE_STRING, len(value))
    return BufferCall('WriteString', [value, buf])


def startArray(buf):
    return encodeIndefiniteLengthType(buf, MAJOR_TYPE_ARRAY)


def startMap(buf):
    return encodeIndefiniteLengthType(buf, MAJOR_TYPE_MAP)


def endSequence(buf):
    return encodeIndefiniteLengthType(buf, MAJOR_TYPE_CONTENT_FREE)