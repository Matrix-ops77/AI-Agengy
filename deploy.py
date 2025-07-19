import subprocess
import sys
import argparse

def run_script(script_name, project_id):
    """Executes a Python script with the project ID as an argument and handles errors."""
    try:
        print(f"--- Running {script_name} for project {project_id} ---")
        process = subprocess.run([sys.executable, script_name, project_id], check=True, capture_output=True, text=True)
        print(process.stdout)
        if process.stderr:
            print("Error output:")
            print(process.stderr)
        print(f"--- Finished {script_name} ---\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

import json

def deploy_date_parser(project_id):
    """Deploys the date parser Cloud Function."""
    print(f"--- Deploying date-parser-helper for project {project_id} ---")
    command = [
        "gcloud", "functions", "deploy", "date-parser-helper",
        "--runtime", "python39",
        "--entry-point", "date_parser_helper",
        "--trigger-http",
        "--allow-unauthenticated",
        "--region", "us-east4",
        "--project", project_id,
        "--source", "./date_parser_helper"
    ]
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print(process.stdout)
        if process.stderr:
            print("Error output:")
            print(process.stderr)
        print("--- Date Parser Deployment Finished ---\n")
    except subprocess.CalledProcessError as e:
        print("Error deploying Date Parser Function:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

def get_function_url(project_id, function_name="date-parser-helper", region="us-east4"):
    """Gets the URL of a deployed Cloud Function."""
    print(f"--- Getting URL for {function_name} ---")
    command = [
        "gcloud", "functions", "describe", function_name,
        "--project", project_id,
        "--region", region,
        "--format=json"
    ]
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        data = json.loads(process.stdout)
        url = data.get("https_trigger", {}).get("url")
        if not url:
            print("Error: Could not retrieve function URL.")
            sys.exit(1)
        print(f"--- Found URL: {url} ---\n")
        return url
    except subprocess.CalledProcessError as e:
        print(f"Error getting function URL for {function_name}:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from gcloud describe: {e}")
        sys.exit(1)

def update_workflow_file(function_url):
    """Replaces the placeholder URL in the workflow file."""
    print(f"--- Updating invoice-processing-workflow.yaml with URL: {function_url} ---")
    with open("invoice-processing-workflow.yaml", "r") as f:
        content = f.read()
    
    content = content.replace("YOUR_DATE_PARSER_FUNCTION_URL", function_url)

    with open("invoice-processing-workflow.yaml", "w") as f:
        f.write(content)
    print("--- Workflow file updated ---\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy the invoice processing project.")
    parser.add_argument("project_id", help="Your Google Cloud project ID.")
    args = parser.parse_args()

    # Define the order of execution
    scripts = [
        "create_gcs_bucket.py",
        "create_bigquery_resources.py",
        "create_documentai_processor.py",
        "create_service_account.py",
        "grant_iam_roles.py",
    ]

    for script in scripts:
        run_script(script, args.project_id)

    deploy_date_parser(args.project_id)
    function_url = get_function_url(args.project_id)
    update_workflow_file(function_url)

    # Now that the workflow is updated, deploy the main trigger function and eventarc trigger
    run_script("create_eventarc_trigger.py", args.project_id)

    print("--- Deployment finished ---")