"""Bigquery API functions, refer to github wiki for more info"""
from google.cloud import bigquery
import uuid

def gcloud_upload(fileobj, input_schema=None, dataset="transaction_log", table_name="base_schema"):
    # Instantiates a client, and corresponding Dataset
    bq_client = bigquery.Client(project = "virtual-bonito-179210")
    dataset = bq_client.dataset(dataset)

    # Create Table instance
    new_table = dataset.table(table_name, schema = input_schema)
    # Reload the table to get the schema.
    # Upload File, overwrite if it exists
    job = new_table.upload_from_file(fileobj,'CSV', num_retries = 1, skip_leading_rows= 1)
    job.begin

def get_bq_schema(dataset = "transaction_log", table_name = "base_schema"):
    # Get schema object of specified table

    bq_client = bigquery.Client(project = "virtual-bonito-179210")
    dataset = bq_client.dataset(dataset)
    table = dataset.table(table_name)
    table.reload()

    return table.schema

def table_from_query(query_string, dataset="transaction_log", table_name="transaction",
                     write_option = "WRITE_APPEND", date_str = ""):
    """
    references :
    https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs
    https://googlecloudplatform.github.io/google-cloud-python/latest/bigquery/usage.html
    datestr should be in yyyymmdd format, UTC
    """
    bq_client = bigquery.Client(project = "virtual-bonito-179210")
    dataset = bq_client.dataset(dataset)

    # Set destination Table
    table = dataset.table(name=table_name+date_str)

    query_job = bq_client.run_async_query(str(uuid.uuid4()), query_string)
    query_job.destination = table
    query_job.use_legacy_sql = False
    query_job.write_disposition = write_option

    # Start Job
    query_job.begin()
    # Wait for job to complete.
    query_job.result()