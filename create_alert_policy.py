from google.cloud import monitoring_v3
from google.api_core.exceptions import AlreadyExists
from google.protobuf import duration_pb2

def create_workflow_failure_alert(project_id):
    client = monitoring_v3.AlertPolicyServiceClient()
    project_name = f"projects/{project_id}"

    # Define the MetricThreshold trigger
    trigger = monitoring_v3.Trigger(
        count=1
    )

    # Define the Aggregation
    aggregation = monitoring_v3.Aggregation(
        alignment_period=duration_pb2.Duration(seconds=60),
        per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE,
    )

    # Define the MetricThreshold condition
    metric_threshold = monitoring_v3.AlertPolicy.Condition.MetricThreshold(
        filter=(
            'resource.type = "workflows.googleapis.com/Workflow" AND '
            'metric.type = "workflows.googleapis.com/execution_count" AND '
            'metric.labels.state = "FAILED"'
        ),
        aggregations=[aggregation],
        comparison=monitoring_v3.ComparisonType.COMPARISON_GT,
        threshold_value=0,
        duration=duration_pb2.Duration(seconds=0),
        trigger=trigger,
    )

    # Define the AlertPolicy Condition
    condition = monitoring_v3.AlertPolicy.Condition(
        display_name="Workflow Failure Rate",
        metric_threshold=metric_threshold
    )

    # Define the AlertPolicy
    policy = monitoring_v3.AlertPolicy(
        display_name="Invoice Processing Workflow Failure Alert",
        combiner=monitoring_v3.AlertPolicy.Combiner.OR,
        conditions=[condition],
        documentation=monitoring_v3.AlertPolicy.Documentation(
            content="This alert fires when the Invoice Processing Workflow fails.",
            mime_type="text/markdown",
        ),
    )

    try:
        print(f"Attempting to create alert policy for project {project_id}...")
        created_policy = client.create_alert_policy(name=project_name, alert_policy=policy)
        print(f"Alert policy created successfully: {created_policy.name}")
        return created_policy
    except AlreadyExists:
        print("Alert policy already exists.")
        return None
    except Exception as e:
        print(f"An error occurred while creating alert policy: {e}")
        return None

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python create_alert_policy.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    create_workflow_failure_alert(project_id)
