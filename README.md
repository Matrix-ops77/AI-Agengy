# AI-Powered Invoice Processing System

This project automates the processing of invoices using Google Cloud services. It uses an Eventarc trigger to invoke a Cloud Function, which in turn triggers a Cloud Workflow that extracts data from invoices using Document AI and stores it in BigQuery.

## Prerequisites

- Google Cloud SDK installed and authenticated.
- Python 3.8+ installed.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure your Google Cloud project ID is set as an environment variable for the Cloud Function (`main.py`).**

## Deployment

Run the deployment script with your project ID as an argument to provision all the necessary Google Cloud resources:

```bash
python deploy.py <your-project-id>
```

This script will:
- Create a GCS bucket for invoices.
- Create a BigQuery dataset and table.
- Create a Document AI processor.
- Create a service account.
- Grant necessary IAM roles.
- Deploy the Cloud Function (`main.py`).
- Create an Eventarc trigger that invokes the Cloud Function.

## Usage

1. Upload an invoice (in PDF format) to the GCS bucket created during deployment.
2. The Eventarc trigger will automatically invoke the Cloud Function.
3. The Cloud Function will then trigger the Cloud Workflow.
4. The workflow will process the invoice and store the extracted data in the BigQuery table.