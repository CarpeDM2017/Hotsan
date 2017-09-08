"""
To be Deprecated :
Merges multiple json file into csv format for past coinone database
"""
from exchange import coinone as coinone
import pandas as pd
import os
import glob

def merge_json():
    # Setting Filename : Filepath & timestamp
    filedir = "\Users\User\Desktop\Coinprice DB"

    # Fetch all json filepath strings
    subfolder_list = os.listdir(filedir)
    for subfolder in subfolder_list :
        filepath = filedir+"\\"+subfolder
        jsonlist = glob.glob(filepath + "\*.json")
        # Initialize temporary json list for each folder
        df_list =[]

        for jsonfile in jsonlist:
            df_tmp = coinone.csv_backfill(open(jsonfile, "r"))
            df_list.append(df_tmp)

        coinone_df = pd.concat(df_list)
        export_filename = os.path.join(filepath, subfolder + ".csv")
        coinone_df.to_csv(path_or_buf = export_filename, index = False)