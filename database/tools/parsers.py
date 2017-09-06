import itertools as it

def payload_parse(payload_dict):
    """Generate combination of payloads generated from input dict
    Returns List of Payloads(Dict). Currently for Coinone only

    Example :
    input =
    {"currency": ["btc", "bch", "eth"], "period": ["hour", "day"]}
    output =
    [{"currency" : "btc", "period" : "hour"},
    {"currency" : "btc", "period" : "day"},
    {"currency" : "bch", "period" : "hour"},
    ....
    {"currency" : "eth", "period" : "day"}]
    """

    try :
        payload_keys = [key for key in payload_dict]
        value_combinations = it.product(*(payload_dict[payload_key] for payload_key in payload_keys))
        payload_combinations = [dict(zip(payload_keys, comb)) for comb in value_combinations]

        return payload_combinations

    except :
        print "Please check whether input data is in correct format"