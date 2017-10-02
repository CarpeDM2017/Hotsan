import httplib2


class HotSanKorbit:
    """
    :description: This is Korbit public and private API class. Request Data and get Result String
    :todo: complete others
    """

    def __init__(self):
        self.url = "https://api.korbit.co.kr/v1/"
        self.request_type = {
                                'final_ticker': 'ticker',
                                'detailed_ticker': 'ticker/detailed',
                                'orderbook': 'orderbook',
                                'transactions': 'transactions',
                                'constraints': 'constants'
                            }
        self.currency_pair = {
                                'btc': 'btc_krw',
                                'eth': 'eth_krw',
                                'etc': 'etc_krw',
                                'xrp': 'xrp_krw',
                            }
        self.time = {
                        'min': 'minute',
                        'hour': 'hour',
                        'day': 'day',
                    }
        
        
    def _get_decode_response_content(self, request_string):
        """
        :param requsest_string: http requset string
        :return (string)content: of http request data
        """
        h = httplib2.Http(".cache")
        resp, content = h.request(request_string, "GET")
        return content.decode('utf-8')
    
    def get_final_ticker(self, currency_pair):
        pass
    
    def get_detailed_ticker(self, currency_pair):
        pass
    
    def get_orderbook(self, currency_pair):
        pass
    
    def get_transactions(self, currency_pair, time="day"):
        """
        :param (str)currnency_pair: coin name.('btc', 'eth', 'etc', 'xrp')
        :param (str)time: range of transaction data you want to get('min', 'hour', (default)'day')
        :return (str)transaction_data: transaction data
        """
        to_request = self.url + self.request_type['transactions']\
                            + '?currency_pair=' \
                            + self.currency_pair[currency_pair]\
                            + '&time=' + self.time[time]
        return self._get_decode_response_content(to_request)
    
        
    def get_constraints(self):
        pass
            
if __name__ == "__main__":
    a = HotSanKorbit()
    print(a.get_transactions('btc')[:100])

