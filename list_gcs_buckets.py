
from google.cloud import storage

def list_buckets(project_id: str):
    """
    Lists all buckets in the given project and specifically checks for 'client-invoices-bucket'.
    """
    storage_client = storage.Client(project=project_id)

    print(f"Listing buckets in project {project_id}...")
    found_target_bucket = False
    try:
        buckets = storage_client.list_buckets()
        for bucket in buckets:
            print(f"  Bucket: {bucket.name} (Location: {bucket.location})")
            if bucket.name == "client-invoices-bucket":
                found_target_bucket = True
                print(f"  CONFIRMED: 'client-invoices-bucket' found! Location: {bucket.location}")

        if not found_target_bucket:
            print("  CONFIRMED: 'client-invoices-bucket' NOT found in the list.")

    except Exception as e:
        print(f"An error occurred while listing buckets: {e}")

if __name__ == "__main__":
    project_id = "ai-invoice-processor-0707"
    list_buckets(project_id)
