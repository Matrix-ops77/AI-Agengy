
from google.cloud import storage
from datetime import datetime

def create_bucket(project_id: str, bucket_name: str, location: str):
    """
    Creates a new Google Cloud Storage bucket.
    """
    storage_client = storage.Client(project=project_id)

    try:
        print(f"Attempting to create bucket: {bucket_name} in {location}...")
        bucket = storage_client.create_bucket(bucket_name, location=location)
        print(f"Bucket {bucket.name} created.")
        return bucket
    except Exception as e:
        print(f"An error occurred while creating bucket: {e}")
        return None

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_gcs_bucket.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    bucket_name = "ai-invoice-processor-0707-invoices" # Fixed bucket name
    location = "us-east4"

    create_bucket(project_id, bucket_name, location)
