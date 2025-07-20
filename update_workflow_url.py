import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python update_workflow_url.py <workflow_file> <url_file>")
        sys.exit(1)

    workflow_file = sys.argv[1]
    url_file = sys.argv[2]

    with open(url_file, 'r') as f:
        url = f.read().strip()

    with open(workflow_file, 'r') as f:
        content = f.read()

    content = content.replace("YOUR_DATE_PARSER_FUNCTION_URL", url)

    with open(workflow_file, 'w') as f:
        f.write(content)

    print(f"Successfully updated {workflow_file} with URL: {url}")

if __name__ == "__main__":
    main()