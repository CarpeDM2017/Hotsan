import simplejson as json
import os
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