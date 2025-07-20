import functions_framework
import flask
from google.cloud import storage
import os
import json


# Initialize Google Cloud Storage client
storage_client = storage.Client()


@functions_framework.http
def move_to_dlq_helper(request: flask.Request):
    """
    HTTP Cloud Function that moves a failed event to a Dead Letter Queue (DLQ)
    bucket.
    This function is intended to be called by a Cloud Workflow or other
    services when an event processing fails.
    """
    # Get the DLQ bucket name from environment variables
    dlq_bucket_name = os.environ.get("DLQ_BUCKET_NAME")
    if not dlq_bucket_name:
        return flask.jsonify({
            "error": "DLQ_BUCKET_NAME environment variable not set."
        }), 500

    request_json = request.get_json(silent=True)
    if not request_json:
        return flask.jsonify({"error": "Invalid request body."}), 400

    # Extract event and error details from the request
    event_data = request_json.get("event")
    error_details = request_json.get("error")

    if not event_data:
        return flask.jsonify({
            "error": "'event' data is missing from the request."
        }), 400

    # Determine the original file path from the event data
    # Assuming event_data contains 'bucket' and 'name' for the original file
    original_bucket_name = event_data.get("bucket")
    original_file_name = event_data.get("name")

    if not original_bucket_name or not original_file_name:
        return flask.jsonify({
            "error": "Original bucket or file name missing in event data."
        }), 400

    # Construct the DLQ file name
    # Appending a timestamp and original file name to avoid overwrites
    timestamp = flask.datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    dlq_file_name = (
        f"failed_event_{timestamp}_{original_file_name}"
    )

    try:
        dlq_bucket = storage_client.bucket(dlq_bucket_name)
        dlq_blob = dlq_bucket.blob(dlq_file_name)

        # Prepare content to write to DLQ (original event + error details)
        dlq_content = {
            "original_event": event_data,
            "error_details": error_details,
            "received_timestamp": timestamp
        }

        dlq_blob.upload_from_string(
            json.dumps(dlq_content),
            content_type="application/json"
        )

        return flask.jsonify({
            "status": "success",
            "dlq_path": (
                f"gs://{dlq_bucket_name}/{dlq_file_name}"
            )
        }), 200

    except Exception as e:
        return flask.jsonify({
            "error": f"Failed to move to DLQ: {e}"
        }), 500
