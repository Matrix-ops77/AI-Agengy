import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
import os

def run_command(command):
    """Executes a command and handles errors."""
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print(process.stdout)
        if process.stderr:
            print("Error output:")
            print(process.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def main(project_id, num_invoices, concurrency):
    """Runs the load test."""
    
    # Generate test data
    print("--- Generating test data ---")
    output_dir = "test_invoices"
    run_command([sys.executable, "generate_test_data.py", str(num_invoices), "--output-dir", output_dir])
    print("--- Test data generation finished ---\n")
    
    # Upload to GCS
    print(f"--- Uploading {num_invoices} invoices to GCS with concurrency {concurrency} ---")
    bucket_name = f"{project_id}-invoices"
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        for i in range(num_invoices):
            file_name = f"invoice_{i+1}.pdf"
            source_file_path = os.path.join(output_dir, file_name)
            executor.submit(upload_blob, bucket_name, source_file_path, file_name)
            
    end_time = time.time()
    
    print(f"--- Upload finished in {end_time - start_time:.2f} seconds ---\n")
    
    print("--- Load test complete. Monitor the results in the Google Cloud Console. ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a load test for the invoice processing pipeline.")
    parser.add_argument("project_id", help="Your Google Cloud project ID.")
    parser.add_argument("num_invoices", type=int, help="The number of invoices to generate and upload.")
    parser.add_argument("--concurrency", type=int, default=10, help="The number of concurrent uploads.")
    args = parser.parse_args()
    
    main(args.project_id, args.num_invoices, args.concurrency)