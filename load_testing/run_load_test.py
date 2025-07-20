import argparse
import requests
import time


def run_load_test(api_url, num_requests, api_key):
    """Runs a load test against the FastAPI backend.
    """
    headers = {"X-API-Key": api_key}
    success_count = 0
    failure_count = 0
    start_time = time.time()

    print(f"Starting load test with {num_requests} requests to {api_url}")

    for i in range(num_requests):
        try:
            # Simulate a file upload by generating a signed URL
            file_name = f"test_invoice_{i}.pdf"
            content_type = "application/pdf"
            response = requests.post(
                f"{api_url}/generate-signed-url/",
                json={
                    "file_name": file_name,
                    "content_type": content_type
                },
                headers=headers
            )
            response.raise_for_status()
            success_count += 1
            print(f"Request {i+1}/{num_requests}: Success")
        except requests.exceptions.RequestException as e:
            failure_count += 1
            print(f"Request {i+1}/{num_requests}: Failure - {e}")

    end_time = time.time()
    duration = end_time - start_time

    print("\nLoad test complete.")
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {success_count}")
    print(f"Failed requests: {failure_count}")
    print(f"Duration: {duration:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a load test against the FastAPI backend."
    )
    parser.add_argument("api_url", type=str,
                        help="The URL of the FastAPI backend.")
    parser.add_argument("num_requests", type=int,
                        help="The number of requests to send.")
    parser.add_argument("api_key", type=str,
                        help="The API key for authentication.")
    args = parser.parse_args()

    run_load_test(args.api_url, args.num_requests, args.api_key)
