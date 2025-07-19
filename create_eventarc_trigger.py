from google.cloud import eventarc_v1
from google.cloud.eventarc_v1.types import Trigger, EventFilter
from google.api_core.exceptions import AlreadyExists, GoogleAPIError

def create_eventarc_trigger(
    project_id: str,
    location: str,
    trigger_id: str,
    destination_cloud_function_service: str,
    destination_cloud_function_region: str,
    gcs_bucket_name: str,
    service_account_email: str,
):
    """
    Creates an Eventarc trigger for a GCS bucket to trigger a Cloud Function.
    """
    client = eventarc_v1.EventarcClient()
    parent = f"projects/{project_id}/locations/{location}"

    trigger = Trigger(
        name=f"{parent}/triggers/{trigger_id}",
        destination=eventarc_v1.Destination(
            cloud_run=eventarc_v1.CloudRun(
                service=destination_cloud_function_service,
                region=destination_cloud_function_region,
            )
        ),
        service_account=service_account_email,
        event_filters=[
            EventFilter(attribute="type", value="google.cloud.storage.object.v1.finalized"),
            EventFilter(attribute="bucket", value=gcs_bucket_name),
        ],
    )

    try:
        print(f"Attempting to create Eventarc trigger: {trigger_id}...")
        operation = client.create_trigger(parent=parent, trigger=trigger, trigger_id=trigger_id)
        result = operation.result()
        print(f"Eventarc trigger created successfully: {result.name}")
        return result
    except AlreadyExists:
        print(f"Eventarc trigger '{trigger_id}' already exists.")
        # If it already exists, we assume it's correctly configured.
        return None
    except GoogleAPIError as e:
        print(f"An API error occurred: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_eventarc_trigger.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    location = "us-east4"
    trigger_id = "trigger-invoice-workflow-gcs"
    destination_cloud_function_service = "trigger-invoice-workflow" # Name of the Cloud Function
    destination_cloud_function_region = "us-east4" # Region of the Cloud Function
    gcs_bucket_name = "ai-invoice-processor-0707-invoices"
    service_account_email = f"eventarc-trigger-sa@{project_id}.iam.gserviceaccount.com"

    create_eventarc_trigger(
        project_id,
        location,
        trigger_id,
        destination_cloud_function_service,
        destination_cloud_function_region,
        gcs_bucket_name,
        service_account_email,
    )