import exchange.coinone as coinone
import tools.formatters as formatters
import tools.bq_tools as bq_tools
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import glob
import shutil

def get_data(payload, file_destination = ""):
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
    payload_list = coinone.payload_parse(payload)

    # Initialize list to contain dataframe of each coin
    df_list =[]

    # Will fetch specified records from server.
    for parsed_payload in payload_list:
        log_df = coinone.get_transaction_log(parsed_payload)
        df_list.list.append(log_df)

    # Merge dataframes of all coins
    coinone_df = pd.concat(df_list)
    formatters.csv_with_timestamp(coinone_df,export_dir=file_destination, filename="Coinone")


# Preset Payloads, Variables
csv_destination = "\Users\User\Desktop\CarpeDM2017\Coinprice_DB"
csv_storage_path = "\Users\User\Desktop\CarpeDM2017\Storage"

payload_dict_daily = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["day"]}
payload_dict_hourly = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["hour"]}

# Get Daily Data, wait for 10 Min
get_data(payload_dict_daily, file_destination= csv_destination)
time.sleep(600)

# Get Hourly Data, wait for 3 min
get_data(payload_dict_hourly, file_destination= csv_destination)
time.sleep(150)

# Get Schema of base table
table_schema = bq_tools.get_bq_schema()

# Get all files in specified Directory
csvlist = glob.glob(csv_destination + "\*.csv")
dataset = "transaction_log"

for csv in csvlist:
    with open(csv, 'rb') as fileobj:
        # Files should be in binary format for google api
        # Extract only filename from filepath
        filename = os.path.splitext(os.path.split(csv)[-1])[0]
        bq_tools.gcloud_upload(fileobj, table_name = filename, input_schema=table_schema)

# Process today's DB, includes Deduping Process
# Get both dates
today = datetime.utcnow()
yesterday = today + timedelta(days=-1)

# Format in string
today = today.strftime("%Y%m%d")
yesterday = yesterday.strftime("%Y%m%d")

# Run Yesterday's Query First, this should be placed first
with open("sql_script\dedupe_yesterday.sql", 'r') as file:
    bq_tools.table_from_query(file.read(), date_str=yesterday)

# Run today's Query
with open("sql_script\dedupe.sql", 'r') as file:
    bq_tools.table_from_query(file.read(), write_option="WRITE_TRUNCATE", date_str=today)

# Move Csv files to Storage Directory
for file in csvlist:
    shutil.move(file, csv_storage_path)

# Remove temporary bigquery tables after process
bq_tools.delete_table(table_name = "temp1",dataset_name="transaction_log")
bq_tools.delete_table(table_name = "temp2",dataset_name="transaction_log")

