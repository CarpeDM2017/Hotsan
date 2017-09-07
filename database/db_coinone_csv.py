"""Script for downloading Coin price DB from coinone server
should run daily, twice on specified time."""

from exchange import coinone as coinone
from tools import parsers
import pandas as pd
import sys
from datetime import datetime
import os

# Setting Filename : Filepath & timestamp
filedir = "\Users\User\Desktop\Coinprice DB"
current_time = datetime.now()
file_timestamp = current_time.strftime('%Y%m%d%H')
filepath_full = os.path.join(filedir, "Coinone" + "_" + file_timestamp + ".csv")

# Specify Which transaction records to fetch as dict format.
payload_dict_daily = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["day"]}
payload_dict_hourly = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["hour"]}

# Check if it's daily request or hourly request
if sys.argv[1] == "hourly":
    payloads = parsers.payload_parse(payload_dict_hourly)
else :
    payloads = parsers.payload_parse(payload_dict_daily)

# Initialize list to contain dataframe of each coin
df_list =[]

# Will fetch specified records from server.
for parsed_payload in payloads:
    Hotsan = coinone.HotSanCoinone(url="trades/", payload=parsed_payload)
    response = Hotsan.get_response(is_public=True)
    record_df = coinone.json_to_df(response)
    df_list.append(record_df)

# Merge dataframes of all coins
coinone_df = pd.concat(df_list)
coinone_df.to_csv(path_or_buf = filepath_full, index = False)