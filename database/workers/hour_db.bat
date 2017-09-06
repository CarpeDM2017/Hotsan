:: This will download coinone transaction records for previous 24 hours
:: For now, windows run this batch file at scheduled time (01AM, 02AM)
@echo off
:: Wait for 15 seconds before starting.
timeout 15
:: Assign parameters, Database to fetch.
SET interval=hourly
python C:\Users\User\Desktop\sunwooang\Hotsan\database\db_coinone.py %interval%