"""
Google Cloud Platform python client
Refer to github wiki page :)
"""
import tools.bq_tools as bq_tools
import os
import glob

# Get all files in specified Directory
filedir = "\Users\User\Desktop\CarpeDM2017\Coinprice_DB"
csvlist = glob.glob(filedir + "\*.csv")
dataset = "transaction_log"

table_schema = bq_tools.get_bq_schema()

for csv in csvlist:
    with open(csv, 'rb') as fileobj: # Files should be in binary format for google api
        # Extract only filename from filepath
        filename = os.path.splitext(os.path.split(csv)[-1])[0]
        bq_tools.gcloud_upload(fileobj, table_name = filename, input_schema=table_schema)

