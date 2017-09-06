# Coded in Python 2.7
import base64
import simplejson as json
import hashlib
import hmac
import httplib2
import urllib
import time

"""
Basic Tools to communicate with Coinone Server. Based on V2 API
Refer to Coinone API Documentation for more info :
http://doc.coinone.co.kr/

Example of Given Parameter formats for V2 API:

ACCESS_TOKEN, SECRET_KEY : GUID string, issued in coinone homepage 
(ex) 'xxx-xxxxxx-xx'

URL = string 
(ex) 'https://api.coinone.co.kr/v2/account/daily_balance/'

PAYLOAD = Json string.
(ex)
{
    "access_token": ACCESS_TOKEN,
    "key1": KEY
}
"""

class HotSanClient:
    def __init__(self, access_token = "", secret_key= "", url= "", payload=None,
                 encoded_payload=None, signature= None):
        """For public Requests, access tokens and secret keys are not required
        encoded payload and signature can ba added by get_encoded_payload() method
        and get_signature() method, which is only necessary for private requests"""
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

    def get_response(self, is_public = False):
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
            return content

        else : # Public Requests does not require encoding
            formatted_url = urllib.urlencode(self.payload)
            response, content = http.request(self.url+'?'+formatted_url, 'GET')
            return content