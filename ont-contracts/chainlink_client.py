from ontology.builtins import sha256, concat
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.interop.System.Action import RegisterAction
from ontology.interop.System.App import DynamicAppCall, RegisterAppCall
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash
from ontology.interop.System.Runtime import CheckWitness, Serialize, Notify
from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.libont import bytearray_reverse
# bb7513b23fae0117eae21eea2cd732e1cc267e7e
AMOUNT_OVERRIDE = 0

SENDER_OVERRIDE = 0

ARGS_VERSION = 1

REQUEST_COUNT = "RequestCount"

ORACLE_ADDRESS = "oracle"
LINK_ADDRESS = "link"

PENDING_REQUESTS_PREFIX = "pendingRequests"

contractHash = GetExecutingScriptHash()

ChainlinkRequestedEvent = RegisterAction("chainlinkRequestedEvent", "requestId")

ChainlinkFulfilledEvent = RegisterAction("chainlinkFulfilledEvent", "requestId")

ChainlinkCancelledEvent = RegisterAction("chainlinkCancelledEvent", "requestId")

ChainlinkCall = RegisterAppCall('db6f26fb0f217d6762aa3d6d38e827789a3128d1', 'operation', 'args')

OWNER = Base58ToAddress("AbG3ZgFrMK6fqwXWR1WkQ1d1EYVunCwknu")

def Main(operation, args):
    if operation == 'buildChainlinkRequest':
        assert (len(args) == 3)
        _specId = args[0]
        callbackAddress = args[1]
        callbackFunction = args[2]
        return buildChainlinkRequest(_specId, callbackAddress, callbackFunction)

    if operation == 'sendChainlinkRequest':
        assert (len(args) == 3)
        caller = args[0]
        req = args[1]
        payment = args[2]
        return sendChainlinkRequest(caller, req, payment)

    if operation == 'sendChainlinkRequestTo':
        assert (len(args) == 4)
        caller = args[0]
        oracle = args[1]
        req = args[2]
        payment = args[3]
        return sendChainlinkRequestTo(caller, oracle, req, payment)

    if operation == 'cancelChainlinkRequest':
        assert (len(args) == 5)
        sender = args[0]
        requestId = args[1]
        payment = args[2]
        callbackFunctionId = args[3]
        expiration = args[4]
        return cancelChainlinkRequest(sender, requestId, payment, callbackFunctionId, expiration)

    if operation == 'setChainlinkOracle':
        assert (len(args) == 1)
        oracle = args[0]
        return setChainlinkOracle(oracle)

    if operation == 'setChainlinkToken':
        assert (len(args) == 1)
        link = args[0]
        return setChainlinkToken(link)

    if operation == 'chainlinkTokenAddress':
        return chainlinkTokenAddress()

    if operation == 'chainlinkOracleAddress':
        return chainlinkOracleAddress()

    if operation == 'addChainlinkExternalRequest':
        assert (len(args) == 2)
        oracle = args[0]
        requestId = args[1]
        return addChainlinkExternalRequest(oracle, requestId)

    if operation == 'recordChainlinkFulfillment':
        assert (len(args) == 2)
        sender = args[0]
        requestId = args[1]
        return recordChainlinkFulfillment(sender, requestId)

    return False


def buildChainlinkRequest(_specId, callbackAddress, callbackFunction):
    return ChainlinkCall('initialize', [_specId, callbackAddress, callbackFunction])


def sendChainlinkRequest(caller, req, payment):
    return sendChainlinkRequestTo(caller, Get(GetContext(), ORACLE_ADDRESS), req, payment)

def sendChainlinkRequestTo(caller, oracle, req, payment):
    RequireWitness(caller)
    requestCount = Get(GetContext(), REQUEST_COUNT)
    requestId = sha256(Serialize([req[1], caller, requestCount]))
    req[3] = requestCount
    Put(GetContext(), concatKey(PENDING_REQUESTS_PREFIX, requestId), oracle)
    ChainlinkRequestedEvent(requestId)
    link = Get(GetContext(), LINK_ADDRESS)

    params = [caller, oracle, payment,
              [SENDER_OVERRIDE, AMOUNT_OVERRIDE, req[0], req[1], req[2], req[3], ARGS_VERSION, req[4], 'oracleRequest']]
    assert (DynamicCallFunction(bytearray_reverse(link), "transferAndCall", params))

    Put(GetContext(), REQUEST_COUNT, requestCount + 1)
    return True


def cancelChainlinkRequest(sender, requestId, payment, callbackFunctionId, expiration):
    RequireWitness(sender)
    oracle = Get(GetContext(), concatKey(PENDING_REQUESTS_PREFIX, requestId))
    params = [sender, requestId, payment, GetCallingScriptHash(), callbackFunctionId, expiration]
    assert (DynamicCallFunction(bytearray_reverse(oracle), "cancelOracleRequest", params))
    Delete(GetContext(), concatKey(PENDING_REQUESTS_PREFIX, requestId))
    ChainlinkCancelledEvent(requestId)
    return True


def setChainlinkOracle(oracle):
    RequireWitness(OWNER)
    assert (len(oracle) == 20)
    Put(GetContext(), ORACLE_ADDRESS, oracle)
    return True


def setChainlinkToken(link):
    RequireWitness(OWNER)
    assert (len(link) == 20)
    Put(GetContext(), LINK_ADDRESS, link)
    return True


def chainlinkTokenAddress():
    return Get(GetContext(), LINK_ADDRESS)


def chainlinkOracleAddress():
    return Get(GetContext(), ORACLE_ADDRESS)


def addChainlinkExternalRequest(oracle, requestId):
    assert (notPendingRequest(requestId))
    Put(GetContext(), concatKey(PENDING_REQUESTS_PREFIX, requestId), oracle)
    return True


## TODO
def useChainlinkWithENS(ens, node):
    return True


## TODO
def updateChainlinkOracleWithENS():
    return True


def recordChainlinkFulfillment(sender, requestId):
    assert (sender == Get(GetContext(), concatKey(PENDING_REQUESTS_PREFIX, requestId)))
    # Notify([sender, Get(GetContext(), concatKey(PENDING_REQUESTS_PREFIX, requestId))])
    Delete(GetContext(), concatKey(PENDING_REQUESTS_PREFIX, requestId))
    ChainlinkFulfilledEvent(requestId)
    return True


def notPendingRequest(requestId):
    assert (not Get(GetContext(), concatKey(PENDING_REQUESTS_PREFIX, requestId)))
    return True


def concatKey(str1, str2):
    return concat(concat(str1, '_'), str2)


def RequireScriptHash(key):
    assert (len(key) == 20)
    return True


def RequireWitness(witness):
    assert (CheckWitness(witness))
    return True


def DynamicCallFunction(callAddress, callbackFunctionId, params):
    res = DynamicAppCall(callAddress, callbackFunctionId, params)
    if res and res == b'\x01':
        return True
    else:
        return False