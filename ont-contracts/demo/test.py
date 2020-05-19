from ontology.builtins import concat
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.interop.System.App import RegisterAppCall, DynamicAppCall
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash
from ontology.interop.System.Runtime import CheckWitness, Notify
from ontology.interop.System.Storage import GetContext, Put, Get
from ontology.libont import bytearray_reverse

CURRENT_PRICE = 'CurrentPrice'

OWNER = Base58ToAddress('AbG3ZgFrMK6fqwXWR1WkQ1d1EYVunCwknu')

ChainlinkCall = RegisterAppCall('ed6bb0abbe24e5603a7f2a5c44e056f3eaeb5949', 'operation', 'args')
ChainlinkClientCall = RegisterAppCall('fb11d3b30a54ae147e86f57d9e554578f68a0041', 'operation', 'args')
Link = RegisterAppCall('bfb52e4b8a5b49099e1ac0ef55789053f2ea347d', 'operation', 'args')
OracleCall = RegisterAppCall('04dc7f8a0ff88de0784ef742650a1d79495565ae', 'operation', 'args')
CBORCall = RegisterAppCall('3f75e2814021abed8a616da8d408d1347cac988f', 'operation', 'args')

ContractAddress = GetExecutingScriptHash()


def Main(operation, args):
    if operation == 'requestEthereumPrice':
        assert (len(args) == 3)
        oracle = args[0]
        jobId = args[1]
        payment = args[2]
        return requestEthereumPrice(oracle, jobId, payment)

    return False


def requestEthereumPrice(oracle, jobId, payment):
    # assert (CheckWitness(OWNER))
    req = ChainlinkClientCall('buildChainlinkRequest', [jobId, ContractAddress, 'fullfill'])
    req = ChainlinkCall('add', [req, "url", "https://etherprice.com/api"])
    req = ChainlinkCall('addStringArray', [req, "path", ["recent", "usd"]])
    # Notify([OWNER, oracle, req, payment])
    assert (ChainlinkClientCall('sendChainlinkRequestTo', [OWNER, oracle, req, payment]))
    return [OWNER, oracle, req, payment]


def addStringArray(request, key, values):
    request = CBORCall('encodeString', [request, key])
    request = CBORCall('startArray', request)
    for value in range(values):
        request = CBORCall('encodeString', [request, value])
    request = CBORCall('endSequence', request)
    return request


def DynamicCallFunction(callAddress, callbackFunctionId, params):
    res = DynamicAppCall(callAddress, callbackFunctionId, params)
    if res and res == b'\x01':
        return True
    else:
        return False


def DynamicCallFunctionResult(callAddress, callbackFunctionId, params):
    return DynamicAppCall(callAddress, callbackFunctionId, params)