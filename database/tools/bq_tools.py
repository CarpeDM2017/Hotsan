"""Bigquery API functions, refer to github wiki for more info"""
from google.cloud import bigquery

def gcloud_upload(fileobj, input_schema=None, dataset="transaction_log", table_name="base_schema"):
    # Instantiates a client, and corresponding Dataset
    bq_client = bigquery.Client(project = "virtual-bonito-179210")
    dataset = bigquery.dataset.Dataset(dataset, bq_client)

    # Create Table instance
    new_table = dataset.table(table_name, schema = input_schema)
    # Reload the table to get the schema.
    # Upload File, overwrite if it exists
    job = new_table.upload_from_file(fileobj,'CSV', num_retries = 1, skip_leading_rows= 1)
    job.begin

def get_bq_schema(dataset = "transaction_log", table_name = "base_schema"):
    # Get schema object of specified table

    bq_client = bigquery.Client(project = "virtual-bonito-179210")
    dataset = bigquery.dataset.Dataset(dataset, bq_client)
    table = dataset.table(table_name)
    table.reload()

    return table.schema