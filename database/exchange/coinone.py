#! ../../hotsan2.7/bin/python2
# -*- coding: utf-8 -*-

"""
Basic Tools to communicate with Coinone Server. Based on V2 API
Refer to Coinone API Documentation for more info :
http://doc.coinone.co.kr/
Last Updated on 20170907
"""

import base64
import hashlib
import hmac
import httplib2
import urllib
import time
import pandas as pd
import simplejson as json
import itertools as it


class HotSanCoinone:
    def __init__(self, access_token="", secret_key="", url="", payload=None,
                 encoded_payload=None, signature=None):
        """For public Requests, access tokens and secret keys are not required
        encoded payload and signature can ba added by get_encoded_payload() method
        and get_signature() method, which is only necessary for private requests

        Example of Given Parameter formats for V2 API:

        ACCESS_TOKEN, SECRET_KEY : GUID string, issued in coinone homepage
        (ex) 'xxx-xxxxxx-xx'

        URL = string
        (ex) 'https://api.coinone.co.kr/v2/account/daily_balance/'

        PAYLOAD = format dict
        (ex)
        {
            "access_token": ACCESS_TOKEN,
            "key1": KEY
        }
        """
        self.access_token = access_token
        self.secret_key = secret_key
        self.url = "https://api.coinone.co.kr/" + url
        self.payload = payload
        self.encoded_payload = encoded_payload
        self.signature = signature

    def get_encoded_payload(self):
        """Encode payload as base64 format and Encrypt signature with given Secret Key"""
        self.payload[u'nonce'] = int(time.time()*1000)
        dumped_json = json.dumps(self.payload)
        self.encoded_payload = base64.b64encode(dumped_json)
        self.signature = hmac.new(str(self.secret_key).upper(), str(self.encoded_payload), hashlib.sha512)

    def get_response(self, is_public = False, return_response = False):
        """Send Payload to URL and Receive response from server
        If it is public request, only send Request URL
        Private Requests must include secret key and access token"""

        http = httplib2.Http()
        if is_public == False: # Private Requests need encoded headers
            headers = {
                'Content-type': 'application/json',
                'X-COINONE-PAYLOAD': self.encoded_payload,
                'X-COINONE-SIGNATURE': self.signature
            }
            response, content = http.request(self.url, 'POST', headers=headers, body=self.encoded_payload)

        else : # Public Requests does not require encoding
            formatted_url = urllib.urlencode(self.payload)
            response, content = http.request(self.url+'?'+formatted_url, 'GET')

        if return_response:
            return content, response

        else :
            return content

def json_to_df(json_string):
    """Exports Coinone Transaction log into dataframe, ready to export as csv
    Sample format of Given transaction logs:
    {
        "errorCode": "0",
        "timestamp": "1504716619",
        "completeOrders": [
            {
                "timestamp": "1504713013", (In seconds)
                "price": "5055500",
                "qty": "0.1648"
            }
        ],
        "result": "success",
        "currency": "btc"
    }
    """
    # Pretty format json
    json_dict = json.loads(json_string)
    # Read Main Content of JSON string, and Cast data type to numeric values.(Original type : string)
    content_list = json_dict["completeOrders"]
    coinone_df = pd.DataFrame(content_list).apply(pd.to_numeric)

    # Add Coin Type, Currency, exchange, timestamp of request. Rename QTY
    coinone_df["coin"] = json_dict["currency"]
    coinone_df["req_timestamp"] = json_dict["timestamp"]
    coinone_df["currency"] = "KRW"
    coinone_df["exchange"] = "coinone"
    coinone_df.rename(columns = {'qty':'volume'}, inplace = True)

    # Order columns
    coinone_df = coinone_df[["timestamp", "exchange", "coin", "price", "currency", "volume", "req_timestamp"]]

    return coinone_df

def payload_parse(payload_dict):
    """Generate combination of payloads generated from input dict
    Returns List of Payloads(Dict).

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

def get_transaction_log(parsed_payload):
    """
    :param parsed_payload: Individual formatted payload in json format
    :return: dataframe format of response
    """
    Hotsan = HotSanCoinone(url="trades/", payload=parsed_payload)
    response = Hotsan.get_response(is_public=True)
    record_df = json_to_df(response)

    return record_df

def is_connected():
    """Check if pc is accessible to coinone server."""
    Hotsan = HotSanCoinone(url="ticker/", payload={"currency": "btc"})
    _, response = Hotsan.get_response(is_public=True, return_response=True)
    # Status 200 is normal. Result will return true if accessible to coinone server
    return "200" == response["status"]

def check_connection(trial=5):
    # Check for internet connection, and proceed if internet is okay. Try 5 Times
    for i in range(trial):
        if is_connected():
            break
        elif i < trial-1:
            time.sleep(10)
        else :
            print "Internet is not connected, please try again"
            exit()
