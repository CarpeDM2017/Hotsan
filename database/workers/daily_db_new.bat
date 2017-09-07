:: This will download coinone transaction records for previous 24 hours
:: For now, windows run this batch file at scheduled time (01AM, 02AM)
@echo off
:: Wait for 15 seconds before starting.
timeout 15
:: Fetch Daily Database (23:55)
python \Users\User\Desktop\sunwooang\Hotsan\database\db_coinone_csv.py daily
:: wait for 10 more minutes
timeout 600
:: Fetch supplementary Database. (Around 00:05)
python \Users\User\Desktop\sunwooang\Hotsan\database\db_coinone_csv.py hourly

