from google.cloud import workflows_v1
from google.cloud.workflows import executions_v1
from google.cloud.workflows.executions_v1.types import Execution
from google.cloud import storage
import os
import json
import requests
import time

def trigger_workflow(event, context):
    """
    Triggered by a change to a Cloud Storage bucket.
    Orchestrates invoice processing, including date parsing and DLQ handling.
    """
    file_name = event['name']
    bucket_name = event['bucket']
    gcs_input_uri = f"gs://{bucket_name}/{file_name}"

    project_id = os.environ.get('GCP_PROJECT_ID', 'ai-invoice-processor-0707')
    location = "us-east4" # Must match the workflow's location
    workflow_id = "invoice-processing-workflow"
    dlq_bucket_name = "ai-invoice-processor-0707-dlq"
    date_parser_function_url = f"https://us-east4-{project_id}.cloudfunctions.net/date-parser-function"

    # Initialize clients
    execution_client = executions_v1.ExecutionsClient()
    storage_client = storage.Client(project=project_id)
    parent = f"projects/{project_id}/locations/{location}/workflows/{workflow_id}"

    parsed_invoice_date = None
    parsed_due_date = None

    # --- Date Parsing (moved from Workflow to Cloud Function) ---
    try:
        # Placeholder: In a real scenario, you'd extract date strings from the invoice
        # before calling the parser. For now, we'll assume they are passed or derived.
        # For demonstration, let's assume we get some date strings from Document AI output
        # or from a pre-processing step. Since we don't have Document AI output here,
        # we'll simulate it or use dummy values for testing the date parser function call.
        # In the actual workflow, Document AI output will be available.
        
        # For now, let's call the date parser with dummy data to test the function call
        # In a real scenario, these would come from Document AI's initial pass
        dummy_invoice_date_str = "2025-07-18"
        dummy_due_date_str = "07/30/2025"

        print(f"Calling date parser for invoice date: {dummy_invoice_date_str}")
        response_invoice_date = requests.post(date_parser_function_url, json={'date_string': dummy_invoice_date_str})
        response_invoice_date.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        parsed_invoice_date = response_invoice_date.json().get('parsed_date')
        print(f"Parsed invoice date: {parsed_invoice_date}")

        print(f"Calling date parser for due date: {dummy_due_date_str}")
        response_due_date = requests.post(date_parser_function_url, json={'date_string': dummy_due_date_str})
        response_due_date.raise_for_status()
        parsed_due_date = response_due_date.json().get('parsed_date')
        print(f"Parsed due date: {parsed_due_date}")

    except requests.exceptions.RequestException as e:
        print(f"Error calling date parser Cloud Function: {e}")
        # Decide if this is a critical failure or if workflow can proceed with null dates
        # For now, we'll proceed with None for dates

    # --- Trigger Workflow ---
    execution_args = {
        "bucket": bucket_name,
        "name": file_name,
        "parsed_invoice_date": parsed_invoice_date,
        "parsed_due_date": parsed_due_date
    }
    execution = Execution()
    execution.argument = json.dumps(execution_args)

    workflow_execution_name = None
    try:
        print(f"Triggering workflow {workflow_id} for file {file_name} in bucket {bucket_name}...")
        response = execution_client.create_execution(parent=parent, execution=execution)
        workflow_execution_name = response.name
        print(f"Workflow execution started: {workflow_execution_name}")

        # --- DLQ Handling (monitoring workflow execution) ---
        # Poll for workflow completion (simplified for example)
        # In production, consider Cloud Tasks or Pub/Sub for async monitoring
        timeout_seconds = 300 # 5 minutes timeout
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout_seconds:
                print(f"Workflow {workflow_execution_name} timed out.")
                raise Exception("Workflow timed out")

            latest_execution = execution_client.get_execution(name=workflow_execution_name)
            if latest_execution.state == Execution.State.SUCCEEDED:
                print(f"Workflow {workflow_execution_name} succeeded.")
                break
            elif latest_execution.state == Execution.State.FAILED:
                print(f"Workflow {workflow_execution_name} failed.")
                raise Exception("Workflow failed")
            
            time.sleep(5) # Poll every 5 seconds

    except Exception as e:
        print(f"Error orchestrating workflow: {e}")
        # --- Move to DLQ ---
        print(f"Moving {gcs_input_uri} to DLQ: gs://{dlq_bucket_name}/{file_name}")
        try:
            source_bucket = storage_client.bucket(bucket_name)
            source_blob = source_bucket.blob(file_name)
            
            dlq_bucket = storage_client.bucket(dlq_bucket_name)
            
            # Copy to DLQ
            source_bucket.copy_blob(source_blob, dlq_bucket, file_name)
            print(f"Copied {file_name} to DLQ.")

            # Delete from original bucket
            source_blob.delete()
            print(f"Deleted {file_name} from original bucket.")

        except Exception as dlq_e:
            print(f"Error moving file to DLQ: {dlq_e}")
        
        # Re-raise the original exception to indicate overall failure of the Cloud Function
        raise
