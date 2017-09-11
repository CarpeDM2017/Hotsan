import tools.bq_tools as bq_tools

filenum =2
csvlist =[1,2]

for csv in csvlist:
    bq_tools.delete_table(table_name = "temp"+str(filenum),dataset_name="transaction_log")
    filenum -= 1