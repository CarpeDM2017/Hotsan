import tools.bq_tools as tools
from datetime import datetime, timedelta

# Get both dates
today = datetime.utcnow()
yesterday = today + timedelta(days=-1)

# Format in string
today = today.strftime("%Y%m%d")
yesterday = yesterday.strftime("%Y%m%d")

# Run Yesterday's Query First, this should be placed first
with open("C:\Users\User\Desktop\Sunwooang\Hotsan\database\workers\dedupe_yesterday.sql", 'r') as file:
    tools.table_from_query(file.read(), date_str=yesterday)

# Run today's Query
with open("C:\Users\User\Desktop\Sunwooang\Hotsan\database\workers\dedupe.sql", 'r') as file:
    tools.table_from_query(file.read(), write_option="WRITE_TRUNCATE", date_str=today)
