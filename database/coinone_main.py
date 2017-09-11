import os
import time
import glob
import shutil
import exchange.coinone as coinone
from tools import formatters as formatters, bq_tools as bq_tools, logger_tools as logger_tools
from datetime import datetime, timedelta
import pandas as pd

def get_data(payload, file_destination = ""):
    # Set Filepath and payloads.
    payload_list = coinone.payload_parse(payload)

    # Initialize list to contain dataframe of each coin
    df_list =[]

    # Will fetch specified records from server.
    for parsed_payload in payload_list:
        log_df = coinone.get_transaction_log(parsed_payload)
        df_list.append(log_df)

    # Merge dataframes of all coins
    coinone_df = pd.concat(df_list)
    formatters.csv_with_timestamp(coinone_df,export_dir=file_destination, filename="Coinone")

if __name__ == "__main__":
    # Initialize logger
    logger = logger_tools.init_logger(filename="Coinone")
    logger.info("Start Coinone DB download")
    try:
        # First, Check whether coinone server is accessible
        coinone.check_connection()
        logger.info("Connection to server Verified")

        # Preset Payloads, Variables
        csv_destination = "\Users\User\Desktop\CarpeDM2017\Coinprice_DB"
        csv_storage_path = "\Users\User\Desktop\CarpeDM2017\Storage"

        payload_dict_daily = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["day"]}
        payload_dict_hourly = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"], "period": ["hour"]}

        # Get Daily Data, wait for 10 Min
        logger.info("Start Downloading daily DB")
        get_data(payload_dict_daily, file_destination= csv_destination)
        logger.info("Downloading Finished, Wait for 10 Min")
        time.sleep(600)

        # Get Hourly Data, wait for 3 min
        get_data(payload_dict_hourly, file_destination= csv_destination)
        logger.info("Downloading Finished, Wait for 3 Min")
        time.sleep(150)

        # Get Schema of base table
        table_schema = bq_tools.get_bq_schema()
        # Get all files in specified Directory
        csvlist = glob.glob(csv_destination + "\*.csv")
        dataset = "transaction_log"
        logger.info("Fetched table schema")

        filenum = 1
        for csv in csvlist:
            with open(csv, 'rb') as fileobj:
                # Files should be in binary format for google api
                # Extract only filename from filepath
                filename = os.path.splitext(os.path.split(csv)[-1])[0]
                bq_tools.gcloud_upload(fileobj, table_name = "temp"+str(filenum), input_schema=table_schema)
                filenum += 1

        logger.info("Uploaded CSV to Bigquery")

        # Process today's DB, includes Deduping Process
        # Get both dates, and format in string
        today = datetime.utcnow()
        yesterday = today + timedelta(days=-1)

        today = today.strftime("%Y%m%d")
        yesterday = yesterday.strftime("%Y%m%d")

        # Run Yesterday's Query First, this should be placed first
        with open("sql_script\dedupe_yesterday.sql", 'r') as file:
            bq_tools.table_from_query(file.read(), date_str=yesterday)
        logger.info("Deduping Process for Yesterday's DB finished")

        # Run today's Query
        with open("sql_script\dedupe.sql", 'r') as file:
            bq_tools.table_from_query(file.read(), write_option="WRITE_TRUNCATE", date_str=today)
        logger.info("Finished formatting Today's DB finished")
        logger.info("Querying Finished")

        # Move Csv files to Storage Directory
        for file in csvlist:
            shutil.move(file, csv_storage_path)
        logger.info("Moved source CSV files to storage")

        # Remove temporary bigquery tables after process
        for csv in csvlist:
            filenum -= 1
            bq_tools.delete_table(table_name = "temp"+str(filenum),dataset_name="transaction_log")
        logger.info("Removed temporary tables from bigquery")
        logger.info("Daily job Finished")

    except:
        logger.exception("Unexpected Error occurred")