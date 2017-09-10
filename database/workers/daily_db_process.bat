:: This will download coinone transaction records for previous 24 hours
:: For now, windows run this batch file at scheduled time (01AM, 02AM)
::@echo off
:: Wait for 15 seconds before starting.
::timeout 15
:: Fetch Daily Database (23:55)
::python \Users\User\Desktop\CarpeDM2017\Hotsan\database\db_coinone_csv.py daily
:: wait for 10 more minutes
::timeout 600
:: Fetch supplementary Database. (Around 00:05)
::python \Users\User\Desktop\CarpeDM2017\Hotsan\database\db_coinone_csv.py hourly

timeout 150

:: Enable delayed variable call in for loop
SETLOCAL EnableDelayedExpansion

:: set variables
set /a counter=1
set "tablename=virtual-bonito-179210:transaction_log."
set "pathname=C:\Users\User\Desktop\CarpeDM2017\Coinprice_DB\"
set "targetdir=C:\Users\User\Desktop\CarpeDM2017\Storage\"
cd C:\Users\User\Desktop\CarpeDM2017\Coinprice_DB\

:: Upload Each file in DB directory to BQ dataset as tmp1, tmp2....
for /f %%f in ('dir /b') do (
    set DatasetName=%tablename%temp!counter!
    set FilePath=%pathname%%%f
    call bq load --autodetect !DatasetName! !FilePath!
    set /a counter+=1
)

:: Process today's db
python C:\Users\User\Desktop\CarpeDM2017\Hotsan\database\bq_daily_table_process.py

:: Move used files to Storage
call move %pathname%*.csv %targetdir%

:: Remove temporary bigquery tables after process
bq rm -t -f transaction_log.temp1
bq rm -t -f transaction_log.temp2
