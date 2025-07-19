from google.cloud import resourcemanager_v3
from google.cloud.resourcemanager_v3.types import SetIamPolicyRequest
from google.iam.v1 import policy_pb2
from google.api_core.exceptions import NotFound

def grant_iam_role_python(project_id: str, service_account_email: str, role: str):
    """
    Grants an IAM role to a service account using the Python client library.
    """
    resource_manager_client = resourcemanager_v3.ProjectsClient()
    
    project_name = f"projects/{project_id}"

    try:
        # Get the current IAM policy
        policy = resource_manager_client.get_iam_policy(request=resourcemanager_v3.GetIamPolicyRequest(resource=project_name))

        # Check if the binding already exists
        binding_exists = False
        for binding in policy.bindings:
            if binding.role == role and f"serviceAccount:{service_account_email}" in binding.members:
                binding_exists = True
                break

        if binding_exists:
            print(f"Role {role} already granted to {service_account_email}.")
            return

        # Add the new binding
        new_binding = policy_pb2.Binding(role=role, members=[f"serviceAccount:{service_account_email}"])
        policy.bindings.append(new_binding)

        # Set the updated IAM policy
        resource_manager_client.set_iam_policy(request=SetIamPolicyRequest(resource=project_name, policy=policy))
        print(f"Role {role} granted to {service_account_email}.")

    except NotFound:
        print(f"Project {project_id} not found.")
    except Exception as e:
        print(f"An error occurred while granting role {role}: {e}")

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grant_iam_roles.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    service_account_email = f"eventarc-trigger-sa@{project_id}.iam.gserviceaccount.com"

    roles_to_grant = [
        "roles/run.invoker",
        "roles/eventarc.publisher",
        "roles/workflowexecutions.editor",
        "roles/storage.objectViewer",
        "roles/documentai.viewer",
        "roles/documentai.editor",
        "roles/bigquery.dataEditor"
    ]

    for role in roles_to_grant:
        grant_iam_role_python(project_id, service_account_email, role)
