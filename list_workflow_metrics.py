from google.cloud import monitoring_v3

def list_workflow_metrics(project_id):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    filter_str = 'metric.type = starts_with("workflows.googleapis.com/")'

    print(f"Listing metrics for project {project_id} with filter: {filter_str}")

    try:
        for descriptor in client.list_metric_descriptors(request=monitoring_v3.ListMetricDescriptorsRequest(name=project_name, filter=filter_str)):
            print(f"\nMetric Type: {descriptor.type}")
            print(f"  Description: {descriptor.description}")
            print(f"  Value Type: {descriptor.value_type}") # Directly use integer value
            print(f"  Metric Kind: {descriptor.metric_kind}") # Directly use integer value
            print("  Labels:")
            for label in descriptor.labels:
                print(f"    - {label.key}: {label.description}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python list_workflow_metrics.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    list_workflow_metrics(project_id)
