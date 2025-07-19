
from google.cloud import bigquery
from google.api_core.exceptions import Conflict

def create_bigquery_dataset_and_table(project_id: str, dataset_id: str, table_id: str):
    """
    Creates a BigQuery dataset and a table with a predefined schema.
    """
    client = bigquery.Client(project=project_id)

    # Create Dataset
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"

    try:
        print(f"Attempting to create dataset: {dataset_id}...")
        dataset = client.create_dataset(dataset)  # Make an API request.
        print(f"Dataset {dataset.dataset_id} created.")
    except Conflict:
        print(f"Dataset {dataset_id} already exists.")
    except Exception as e:
        print(f"An error occurred while creating dataset: {e}")
        return

    # Define Table Schema
    schema = [
        bigquery.SchemaField("vendor_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("invoice_date", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("due_date", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("total_amount", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("processed_timestamp", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("source_file_path", "STRING", mode="NULLABLE"),
    ]

    table_ref = dataset_ref.table(table_id)
    table = bigquery.Table(table_ref, schema=schema)

    # Create Table
    try:
        print(f"Attempting to create table: {table_id} in dataset {dataset_id}...")
        table = client.create_table(table)  # Make an API request.
        print(f"Table {table.table_id} created.")
    except Conflict:
        print(f"Table {table_id} already exists in dataset {dataset_id}.")
    except Exception as e:
        print(f"An error occurred while creating table: {e}")

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_bigquery_resources.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    dataset_id = "automation_outputs"
    table_id = "processed_invoices"

    create_bigquery_dataset_and_table(project_id, dataset_id, table_id)
