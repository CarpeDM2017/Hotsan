:: to be deprecated
@echo off
:: Enable delayed variable call in for loop
SETLOCAL EnableDelayedExpansion

set /a counter=1
set "tablename=virtual-bonito-179210:transaction_log."
set "pathname=C:\Users\User\Desktop\Sunwooang\Coinprice_DB\"
set "targetdir=C:\Users\User\Desktop\Sunwooang\Storage\"
cd C:\Users\User\Desktop\Sunwooang\Coinprice_DB\

:: Upload Each file in DB directory to BQ dataset as tmp1, tmp2....
for /f %%f in ('dir /b') do (
    set DatasetName=%tablename%temp!counter!
    set FilePath=%pathname%%%f
    call bq load --autodetect !DatasetName! !FilePath!
    set /a counter+=1
)

:: Make Today's DB
python C:\Users\User\Desktop\Sunwooang\Hotsan\database\bq_daily_table.py

:: Move used files to Storage
call move %pathname%*.csv %targetdir%

:: Remove temp tables after process
bq rm -t -f transaction_log.temp1
bq rm -t -f transaction_log.temp2