import exchange.coinone as coinone
import tools.formatters as formatters
import pandas as pd
from datetime import datetime
import os
import time

def get_data(payload):
    # Check for internet connection, and proceed if internet is okay. Try 5 Times
    for i in range(5):
        if coinone.is_connected():
            break
        elif i < 4:
            time.sleep(10)
        else :
            print "Internet is not connected, please try again"
            exit()

    # Set Filepath and payloads.
    csv_destination = "\Users\User\Desktop\CarpeDM2017\Coinprice_DB"
    payload_list = coinone.payload_parse(payload)

    # Initialize list to contain dataframe of each coin
    df_list =[]

    # Will fetch specified records from server.
    for parsed_payload in payload_list:
        log_df = coinone.get_transaction_log(parsed_payload)
        df_list.list.append(log_df)

    # Merge dataframes of all coins
    coinone_df = pd.concat(df_list)
    formatters.csv_with_timestamp(coinone_df,export_dir=csv_destination, filename="Coinone")


# Preset Payloads
payload_dict_daily = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["day"]}
payload_dict_hourly = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["hour"]}

get_data(payload_dict_daily)
time.sleep(600)
get_data(payload_dict_hourly)
time.sleep(150)

## 이 아래로 빅쿼리 거시기 머시기 하기.

