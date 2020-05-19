from ontology.builtins import concat, sha256
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.interop.System.Action import RegisterAction
from ontology.interop.System.App import DynamicAppCall
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash
from ontology.interop.System.Runtime import CheckWitness, GetTime, Notify, Serialize
from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.libont import bytearray_reverse

# cd6fb4678612081f272052e949ef2309f181e91b
EXPIRY_TIME = 30

INITIALIZED = "INIT"
MINIMUM_CONSUMER_GAS_LIMIT = 100000000
OWNER = Base58ToAddress("AbG3ZgFrMK6fqwXWR1WkQ1d1EYVunCwknu")
LINKTOKEN_ADDRESS = 'linktokenAddress'
COMMITMENTS_PRIFX = 'commitments'
AUTHORIZE_NODES_PREFIX = 'authorizeNodes'
WITHDRAWABLETOKENS = 'withdrawableTokens'

ContractAddress = GetExecutingScriptHash()

CancelOracleRequestEvent = RegisterAction("cancelOracleRequest", "requestId")

OracleRequestEvent = RegisterAction("oracleRequest", "specId", "sender", "requestId", "payment", "callbackAddress",
                                    "callbackFunctionId", "expiration", "dataVersion", "data", "callFunctionId")


def Main(operation, args):
    if operation == 'init':
        assert (len(args) == 1)
        link = args[0]
        return init(link)

    if operation == 'oracleRequest':
        assert (len(args) == 9)
        spender = args[0]
        payment = args[1]
        specId = args[2]
        callbackAddress = args[3]
        callbackFunctionId = args[4]
        nonce = args[5]
        dataVersion = args[6]
        data = args[7]
        callFunctionId = args[8]
        return oracleRequest(spender, payment, specId, callbackAddress, callbackFunctionId, nonce, dataVersion,
                             data, callFunctionId)

    if operation == 'fulfillOracleRequest':
        assert (len(args) == 7)
        node = args[0]
        requestId = args[1]
        payment = args[2]
        callbackAddress = args[3]
        callbackFunctionId = args[4]
        expiration = args[5]
        data = args[6]
        return fulfillOracleRequest(node, requestId, payment, callbackAddress, callbackFunctionId, expiration, data)

    if operation == 'getAuthorizationStatus':
        assert (len(args) == 1)
        node = args[0]
        return getAuthorizationStatus(node)

    if operation == 'setFulfillmentPermission':
        assert (len(args) == 2)
        node = args[0]
        allowed = args[1]
        return setFulfillmentPermission(node, allowed)

    if operation == 'withdraw':
        assert (len(args) == 2)
        recipient = args[0]
        amount = args[1]
        return withdraw(recipient, amount)

    if operation == 'withdrawable':
        return withdrawable()

    if operation == 'cancelOracleRequest':
        assert (len(args) == 6)
        sender = args[0]
        requestId = args[1]
        payment = args[2]
        callbackAddress = args[3]
        callbackFunctionId = args[4]
        expiration = args[5]
        return cancelOracleRequest(sender, requestId, payment, callbackAddress, callbackFunctionId, expiration)

    if operation == 'onTokenTransfer':
        assert (len(args) == 3)
        spender = args[0]
        amount = args[1]
        data = args[2]
        return onTokenTransfer(spender, amount, data)

    if operation == 'getChainLinkToken':
        return getChainLinkToken()
    return True


def init(link):
    RequireWitness(OWNER)
    # inited = Get(GetContext(), INITIALIZED)
    # if inited:
    #     Notify(["idiot admin, you have initialized the contract"])
    #     return False
    # else:
    Put(GetContext(), INITIALIZED, 1)
    Put(GetContext(), LINKTOKEN_ADDRESS, link)
    Notify(["Initialized contract successfully!!!!!!!!"])
    return True


def oracleRequest(spender, payment, specId, callbackAddress, callbackFunctionId, nonce, dataVersion, data,
                  callFunctionId):
    onlyLINK()
    RequireWitness(spender)
    payment = payment + 0
    # TODO
    requestId = sha256(Serialize([callbackAddress, spender, nonce]))
    assert (not Get(GetContext(), concatKey(COMMITMENTS_PRIFX, requestId)))
    expiration = GetTime() + EXPIRY_TIME
    Put(GetContext(), concatKey(COMMITMENTS_PRIFX, requestId),
        Serialize([payment, callbackAddress, callbackFunctionId, expiration]))
    OracleRequestEvent(specId, spender, requestId, payment, callbackAddress, callbackFunctionId, expiration,
                       dataVersion, data, callFunctionId)
    return True


def fulfillOracleRequest(node, requestId, payment, callbackAddress, callbackFunctionId, expiration, data):
    RequireWitness(node)
    onlyAuthorizedNode(node)
    expiration = expiration + 0
    payment = payment + 0
    paramsHash = Serialize([payment, callbackAddress, callbackFunctionId, expiration])
    assert (Get(GetContext(), concatKey(COMMITMENTS_PRIFX, requestId)) == paramsHash)

    Put(GetContext(), WITHDRAWABLETOKENS, Get(GetContext(), WITHDRAWABLETOKENS) + payment)
    Delete(GetContext(), concatKey(COMMITMENTS_PRIFX, requestId))
    assert (callBackFunction(callbackAddress, callbackFunctionId, requestId, data))
    return True


def getAuthorizationStatus(node):
    return Get(GetContext(), concatKey(AUTHORIZE_NODES_PREFIX, node))


def setFulfillmentPermission(node, allowed):
    RequireWitness(OWNER)
    Put(GetContext(), concatKey(AUTHORIZE_NODES_PREFIX, node), allowed)
    return True


# 取回合约中存储的LINK TOKEN
def withdraw(recipient, amount):
    RequireWitness(OWNER)
    hasAvailableFunds(amount)
    assert (_transferLinkFromContact(Get(GetContext(), LINKTOKEN_ADDRESS), recipient, amount))
    return True


# 返回合约中可取回的LINK TOKEN
def withdrawable():
    return Get(GetContext(), WITHDRAWABLETOKENS)


# 取消oracle服务请求
def cancelOracleRequest(sender, requestId, payment, callbackAddress, callbackFunctionId, expiration):
    RequireWitness(sender)
    expiration = expiration + 0
    payment = payment + 0

    paramsHash = Serialize([payment, callbackAddress, callbackFunctionId, expiration])

    originParamsHash = Get(GetContext(), concatKey(COMMITMENTS_PRIFX, requestId))
    assert (paramsHash == originParamsHash)
    # Notify([originParamsHash, paramsHash, sender, requestId, payment, callbackAddress, callbackFunctionId, expiration])
    assert (expiration <= GetTime())
    Delete(GetContext(), concatKey(COMMITMENTS_PRIFX, requestId))

    assert (_transferLinkFromContact(bytearray_reverse(getChainLinkToken()), callbackAddress, payment))
    return True


# 获取LINK地址
def getChainLinkToken():
    return Get(GetContext(), LINKTOKEN_ADDRESS)


def hasAvailableFunds(amount):
    availableFunds = Get(GetContext(), WITHDRAWABLETOKENS)
    assert (availableFunds > 0 and availableFunds >= amount)
    return True


def isValidRequest(requestId):
    assert (Get(GetContext(), concatKey(COMMITMENTS_PRIFX, requestId)))
    return True


def onlyAuthorizedNode(node):
    assert (Get(GetContext(), concatKey(AUTHORIZE_NODES_PREFIX, node)) or node == OWNER)
    return True


def onlyLINK():
    assert (bytearray_reverse(GetCallingScriptHash()) == getChainLinkToken())
    return True


def onTokenTransfer(spender, amount, data):
    onlyLINK()
    # validRequestLength(data)
    permittedFunctionsForLINK(data)
    data[0] = spender
    data[1] = amount
    assert (oracleRequest(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
    return True


def permittedFunctionsForLINK(data):
    assert ("oracleRequest" == data[8])
    return True


def validRequestLength(data):
    assert (len(data) >= 8)
    return True


def RequireScriptHash(key):
    assert (len(key) == 20)
    return True


def RequireWitness(witness):
    assert (CheckWitness(witness))
    return True


def concatKey(str1, str2):
    return concat(concat(str1, '_'), str2)


def _transferLinkFromContact(link, toAcct, amount):
    params = [ContractAddress, toAcct, amount]
    res = DynamicAppCall(link, 'transfer', params)
    if res and res == b'\x01':
        return True
    else:
        return False


def _transferLink(link, fromAcct, toAcct, amount):
    """
    transfer _transferOEP4
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    RequireWitness(fromAcct)
    params = [fromAcct, toAcct, amount]
    res = DynamicAppCall(link, 'transfer', params)
    if res and res == b'\x01':
        return True
    else:
        return False


def callBackFunction(callbackAddress, callbackFunctionId, requestId, data):
    params = [requestId, data]
    res = DynamicAppCall(callbackAddress, callbackFunctionId, params)
    if res and res == b'\x01':
        return True
    else:
        return False