from exchange import coinone_api as coinone
from tools import formatters
from tools import parsers

"""Script for downloading Coin price DB from coinone server
should run daily on specified time."""

# Specify Which transaction records to fetch as dict format.
payload_dict_raw = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["day"]}
payloads = parsers.payload_parse(payload_dict_raw)

# Will fetch specified records from server.
for parsed_payload in payloads:
    Hotsan = coinone.HotSanClient(url="trades/", payload=parsed_payload)
    response = Hotsan.get_response(is_public=True)
    formatters.json_to_file(response, filename=parsed_payload["currency"], filepath_dir= "\Users\User\Desktop\Coinprice DB")