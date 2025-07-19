
from google.cloud import iam_admin_v1
from google.api_core.exceptions import AlreadyExists

def create_service_account_python(project_id: str, service_account_id: str, display_name: str):
    """
    Creates a service account using the Python client library.
    """
    client = iam_admin_v1.IAMClient()
    project_name = f"projects/{project_id}"

    # Create the ServiceAccount object with just the display name
    service_account = iam_admin_v1.ServiceAccount(
        display_name=display_name
    )

    try:
        print(f"Attempting to create service account: {service_account_id}...")
        response = client.create_service_account(
            name=project_name, # This is the parent project name
            service_account_id=service_account_id, # This is the string ID for the SA
            service_account=service_account # This is the ServiceAccount object
        )
        print(f"Service account {response.email} created.")
        return response.email
    except AlreadyExists:
        print(f"Service account {service_account_id} already exists.")
        # If it already exists, retrieve its email
        existing_sa = client.get_service_account(name=f"{project_name}/serviceAccounts/{service_account_id}@{project_id}.iam.gserviceaccount.com")
        return existing_sa.email
    except Exception as e:
        print(f"An error occurred while creating service account: {e}")
        return None

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_service_account.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    service_account_id = "eventarc-trigger-sa"
    display_name = "Eventarc Trigger Service Account"

    email = create_service_account_python(project_id, service_account_id, display_name)
    if email:
        print(f"Service account email: {email}")
    else:
        print("Failed to create or retrieve service account.")
