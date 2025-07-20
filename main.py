from google.cloud import workflows_v1
from google.cloud.workflows import executions_v1
from google.cloud.workflows.executions_v1.types import Execution
import os
import json

def trigger_workflow(event, context):
    """
    A simple Cloud Function that triggers the invoice processing workflow.
    The event payload is passed directly to the workflow.
    """
    print(f"File {event['name']} uploaded to bucket {event['bucket']}. Triggering workflow.")

    project_id = os.environ.get('GCP_PROJECT_ID')
    processor_id = os.environ.get('PROCESSOR_ID')
    dlq_url = os.environ.get('DLQ_URL')
    location = "us-east4"
    workflow_id = "invoice-processing-workflow"

    if not all([project_id, processor_id, dlq_url]):
        raise EnvironmentError("Missing required environment variables: GCP_PROJECT_ID, PROCESSOR_ID, DLQ_URL")

    execution_client = executions_v1.ExecutionsClient()
    parent = f"projects/{project_id}/locations/{location}/workflows/{workflow_id}"

    # Pass the GCS event and other parameters to the workflow
    execution = Execution(argument=json.dumps({
        "event": event,
        "project_id": project_id,
        "processor_id": processor_id,
        "dlq_url": dlq_url
    }))

    try:
        response = execution_client.create_execution(parent=parent, execution=execution)
        print(f"Workflow execution started: {response.name}")
    except Exception as e:
        print(f"Error triggering workflow: {e}")
        # Re-raise the exception to ensure the function execution is marked as a failure
        raise
