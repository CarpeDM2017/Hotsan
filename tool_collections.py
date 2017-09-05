# todo/ add Ticker Receier: iterate N times with x interval
import simplejson as json
import itertools as it
import os
from datetime import datetime

def json_to_file(json_object, filename="Dataset", filepath_dir = "", add_timestamp = True):
    """Pretty prints json response as file"""
    # Pretty format json
    parsed = json.loads(json_object)
    # Check whether to add timestamp to filename
    if add_timestamp is True:
        current_time = datetime.now()
        file_timestamp = current_time.strftime('%Y%m%d%H%M%S')
    else :
        file_timestamp = ""

    # Write json to designated filepath
    filepath_result = os.path.join(filepath_dir, filename + "_" + file_timestamp + ".json")
    fd = open(filepath_result, 'w')
    fd.write(json.dumps(parsed, indent=4))
    fd.close()

def payload_parse(payload_dict):
    """Generate combination of payloads generated from input dict
    Returns List of Payloads(Dict)

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