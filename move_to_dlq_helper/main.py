import functions_framework
import flask
import google.cloud.storage as storage
import json
import os

@functions_framework.http
def move_to_dlq_helper(request: flask.Request):
    """
    An HTTP-triggered Cloud Function to move a failed invoice to the DLQ bucket.
    """
    request_json = request.get_json(silent=True)
    
    if not request_json or 'event' not in request_json or 'error' not in request_json:
        return flask.jsonify({"error": "Invalid request. 'event' and 'error' are required."}), 400

    event = request_json['event']
    error = request_json['error']
    
    project_id = os.environ.get('GCP_PROJECT_ID', 'ai-invoice-processor-0707')
    dlq_bucket_name = f"{project_id}-invoices-dlq"
    
    source_bucket_name = event['bucket']
    file_name = event['name']

    storage_client = storage.Client(project=project_id)

    try:
        source_bucket = storage_client.bucket(source_bucket_name)
        source_blob = source_bucket.blob(file_name)
        
        dlq_bucket = storage_client.bucket(dlq_bucket_name)
        
        # Copy to DLQ
        source_bucket.copy_blob(source_blob, dlq_bucket, file_name)
        
        # Delete from original bucket
        source_blob.delete()

        # Log the error and the move to DLQ
        log_message = {
            "message": f"Moved {file_name} to DLQ bucket {dlq_bucket_name}.",
            "original_event": event,
            "workflow_error": error
        }
        print(json.dumps(log_message))

        return flask.jsonify({"status": "success", "message": f"Moved {file_name} to DLQ."})

    except Exception as e:
        error_message = {
            "message": f"Error moving file to DLQ: {e}",
            "original_event": event,
            "workflow_error": error
        }
        print(json.dumps(error_message))
        return flask.jsonify({"status": "error", "message": str(e)}), 500