#! hotsan2.7/bin/python2
# -*- coding: utf-8 -*-

import os
import time
import glob
import shutil
from datetime import datetime, timedelta
import pandas as pd
from tools import formatters as formatters, bq_tools as bq_tools, logger_tools as logger_tools
import exchange.coinone as coinone


def get_data(payload, file_destination=""):
    """TODO:Docstring
    :param payload
    :param file_destination
    :return none
    """
    # Set Filepath and payloads.
    payload_list = coinone.payload_parse(payload)

    # Initialize list to contain dataframe of each coin
    df_list = []

    # Will fetch specified records from server.
    for parsed_payload in payload_list:
        log_df = coinone.get_transaction_log(parsed_payload)
        df_list.append(log_df)

    # Merge dataframes of all coins
    coinone_df = pd.concat(df_list)
    formatters.csv_with_timestamp(coinone_df, export_dir=file_destination, filename="Coinone")

if __name__ == "__main__":
    # Initialize LOGGER
    LOGGER = logger_tools.init_LOGGER(filename="Coinone")
    LOGGER.info("Start Coinone DB download")
    try:
        # First, Check whether coinone server is accessible
        coinone.check_connection()
        LOGGER.info("Connection to server Verified")

        # Preset Payloads, Variables
        CSV_DESTINATION = os.path.join(os.path.expanduser("~"),\
                                        "Desktop",\
                                        "CarpeDM2017",\
                                        "Coinprice_DB")
        CSV_STORAGE_PATH = os.path.join(os.path.expanduser("~"),\
                                        "Desktop",\
                                        "CarpeDM2017",\
                                        "Storage")

        PAYLOAD_DICT_DAILY = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"],\
                                "period": ["day"]}
        PAYLOAD_DICT_HOURLY = {"currency": ["btc", "bch", "eth", "xrp", "etc", "qtum"],\
                                "period": ["hour"]}

        # Get Daily Data, wait for 10 Min
        LOGGER.info("Start Downloading daily DB")
        get_data(PAYLOAD_DICT_DAILY, file_destination=CSV_DESTINATION)
        LOGGER.info("Downloading Finished, Wait for 10 Min")
        time.sleep(600)

        # Get Hourly Data, wait for 3 min
        get_data(PAYLOAD_DICT_HOURLY, file_destination=CSV_DESTINATION)
        LOGGER.info("Downloading Finished, Wait for 3 Min")
        time.sleep(150)

        # Get Schema of base table
        TABLE_SCHEMA = bq_tools.get_bq_schema()
        # Get all files in specified Directory
        CSVLIST = glob.glob(os.path.join(CSV_DESTINATION, "*.csv"))
        DATASET = "transaction_log"
        LOGGER.info("Fetched table schema")

        FILENUM = 1
        for csv in CSVLIST:
            with open(csv, 'rb') as fileobj:
                # Files should be in binary format for google api
                # Extract only filename from filepath
                filename = os.path.splitext(os.path.split(csv)[-1])[0]
                bq_tools.gcloud_upload(fileobj, table_name="temp" + str(FILENUM), input_schema=TABLE_SCHEMA)
                FILENUM += 1

        LOGGER.info("Uploaded CSV to Bigquery")
        time.sleep(60)

        # Process TODAY's DB, includes Deduping Process
        # Get both dates, and format in string
        TODAY_UNIX = datetime.utcnow()
        YESTERDAY_UNIX = TODAY_UNIX + timedelta(days=-1)

        TODAY = TODAY_UNIX.strftime("%Y%m%d")
        YESTERDAY = YESTERDAY_UNIX.strftime("%Y%m%d")

        # Run YESTERDAY's Query First, this should be placed first
        with open(os.path.join(os.path.dirname(__file__), "sql_script", "dedupe_YESTERDAY.sql"), 'r') as file:
            bq_tools.table_from_query(file.read(), date_str=YESTERDAY)
        LOGGER.info("Deduping Process for YESTERDAY's DB finished")

        # Run TODAY's Query
        with open(os.path.join(os.path.dirname(__file__), "sql_script", "dedupe.sql"), 'r') as file:
            bq_tools.table_from_query(file.read(), write_option="WRITE_TRUNCATE", date_str=TODAY)
        LOGGER.info("Finished formatting TODAY's DB finished")
        LOGGER.info("Querying Finished")

        # Move Csv files to Storage Directory
        for file in CSVLIST:
            shutil.move(file, CSV_STORAGE_PATH)
        LOGGER.info("Moved source CSV files to storage")

        # Remove temporary bigquery tables after process
        for csv in CSVLIST:
            FILENUM -= 1
            bq_tools.delete_table(table_name="temp"+str(FILENUM), DATASET_name="transaction_log")
        LOGGER.info("Removed temporary tables from bigquery")
        LOGGER.info("Daily job Finished")

    except: #TODO: Specify Error
        LOGGER.exception("Unexpected Error occurred")
