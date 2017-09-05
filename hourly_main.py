import coinone_tools
import tool_collections

payload_dict_raw = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["hour"]}
payloads = tool_collections.payload_parse(payload_dict_raw)

for parsed_payload in payloads:
    Hotsan = coinone_tools.HotSanClient(url="trades/", payload=parsed_payload)
    response = Hotsan.get_response(is_public=True)
    tool_collections.json_to_file(response, filename=parsed_payload["currency"], filepath_dir= "\Users\User\Desktop\Coinprice DB")