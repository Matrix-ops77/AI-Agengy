import subprocess
import sys

def run_script(script_name, project_id):
    """Runs a Python script with the project ID as an argument."""
    try:
        subprocess.run(["python", script_name, project_id], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: {script_name} not found.")
        sys.exit(1)

def main():
    """Main function to deploy the invoice processing system."""
    if len(sys.argv) != 2:
        print("Usage: python deploy.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]

    # --- Resource Creation ---
    print("--- Creating GCS Bucket ---")
    run_script("create_gcs_bucket.py", project_id)

    print("\n--- Creating BigQuery Resources ---")
    run_script("create_bigquery_resources.py", project_id)

    print("\n--- Creating Document AI Processor ---")
    run_script("create_documentai_processor.py", project_id)

    print("\n--- Creating Service Account ---")
    run_script("create_service_account.py", project_id)

    # --- IAM Configuration ---
    print("\n--- Granting IAM Roles ---")
    run_script("grant_iam_roles.py", project_id)

    # --- Eventarc Trigger ---
    print("\n--- Creating Eventarc Trigger ---")
    run_script("create_eventarc_trigger.py", project_id)
    
    # --- Monitoring ---
    print("\n--- Creating Alert Policy ---")
    run_script("create_alert_policy.py", project_id)

    print("\n--- Deployment Complete ---")

if __name__ == "__main__":
    main()
