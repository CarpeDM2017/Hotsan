# -*- coding: utf-8 -*-

import simplejson as json
import os
import pandas as pd
from datetime import datetime

def json_to_file(json_object, filename="Dataset", filepath_dir = "", add_timestamp = True):
    """Pretty prints json response as file"""
    # Pretty format json
    parsed = json.loads(json_object)
    # Check whether to add timestamp to filename
    if add_timestamp is True:
        current_time = datetime.now()
        file_timestamp = current_time.strftime('%Y%m%d%H%M%S')
    else :
        file_timestamp = ""

    # Write json to designated filepath
    filepath_result = os.path.join(filepath_dir, filename + "_" + file_timestamp + ".json")
    fd = open(filepath_result, 'w')
    fd.write(json.dumps(parsed, indent=4))
    fd.close()

def csv_with_timestamp(df, export_dir = os.path.join(os.path.expanduser("~")), filename="Data", log_time=True, include_index=False):
    """
    :param df: Dataframe to convert to csv file
    :param log_time: to log time on export filename or not
    :param include_index:  to include dataframe index or not
    """
    # Get Current Timestamp in specified format
    if log_time:
        current_time = datetime.now()
        file_timestamp = current_time.strftime('%Y%m%d%H%M%S')
    else :
        file_timestamp = ""

    filepath_full = os.path.join(export_dir, filename+"_"+file_timestamp+".csv")

    try :
        df.to_csv(path_or_buf = filepath_full, index = include_index)
    except :
        print "input \"df\" should be in Pandas dataframe"
