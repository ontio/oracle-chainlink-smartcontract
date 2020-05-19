############ Chainlink Library#########
from ontology.interop.System.App import RegisterAppCall

defaultBufferSize = 256
BufferCall = RegisterAppCall('d5f12664535717af51f52fe2aa88a18d327ea1b9', 'operation', 'args')
CBORCall = RegisterAppCall('3f75e2814021abed8a616da8d408d1347cac988f', 'operation', 'args')


def Main(operation, args):
    if operation == 'initialize':
        assert (len(args) == 3)
        id = args[0]
        callbackAddress = args[1]
        callbackFunction = args[2]
        return initialize(id, callbackAddress, callbackFunction)

    if operation == 'setBuffer':
        assert (len(args) == 2)
        request = args[0]
        data = args[1]
        return setBuffer(request, data)

    if operation == 'add':
        assert (len(args) == 3)
        request = args[0]
        key = args[1]
        value = args[2]
        return add(request, key, value)

    if operation == 'addBytes':
        assert (len(args) == 3)
        request = args[0]
        key = args[1]
        value = args[2]
        return addBytes(request, key, value)

    if operation == 'addUInt':
        assert (len(args) == 3)
        request = args[0]
        key = args[1]
        value = args[2]
        return addUInt(request, key, value)

    if operation == 'addInt':
        assert (len(args) == 3)
        request = args[0]
        key = args[1]
        value = args[2]
        return addInt(request, key, value)

    if operation == 'addStringArray':
        assert (len(args) == 3)
        request = args[0]
        key = args[1]
        values = args[2]
        return addStringArray(request, key, values)

    return True


def initialize(id, callbackAddress, callbackFunction):
    return [id, callbackAddress, callbackFunction, 0, None]


def setBuffer(request, data):
    request[4] = BufferCall('WriteBytes', [data, request[4]])
    return [request[0], request[1], request[2], request[3], request[4]]


def add(request, key, value):
    request[4] = CBORCall('encodeString', [request[4], key])
    request[4] = CBORCall('encodeString', [request[4], value])
    return [request[0], request[1], request[2], request[3], request[4]]


def addBytes(request, key, value):
    request[4] = CBORCall('encodeString', [request[4], key])
    request[4] = CBORCall('encodeBytes', [request[4], value])
    return [request[0], request[1], request[2], request[3], request[4]]


def addInt(request, key, value):
    request[4] = CBORCall('encodeString', [request[4], key])
    request[4] = CBORCall('encodeInt', [request[4], value])
    return [request[0], request[1], request[2], request[3], request[4]]


def addUInt(request, key, value):
    request[4] = CBORCall('encodeString', [request[4], key])
    request[4] = CBORCall('encodeUInt', [request[4], value])
    return [request[0], request[1], request[2], request[3], request[4]]


def addStringArray(request, key, values):
    request[4] = CBORCall('encodeString', [request[4], key])
    request[4] = CBORCall('startArray', [request[4]])
    for i in range(len(values)):
        request[4] = CBORCall('encodeString', [request[4], values[i]])
    request[4] = CBORCall('endSequence', [request[4]])
    return [request[0], request[1], request[2], request[3], request[4]]
