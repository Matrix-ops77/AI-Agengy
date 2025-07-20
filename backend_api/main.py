from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from google.cloud import storage
import os
from dotenv import load_dotenv
import logging


# Load environment variables from .env file
load_dotenv()

app = FastAPI()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configure Google Cloud Storage
BUCKET_NAME = os.environ.get(
    "GCS_BUCKET_NAME", "ai-invoice-processor-0707-invoices"
)
storage_client = storage.Client()


# API Key authentication
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    logger.error("API_KEY environment variable not set.")
    raise ValueError("API_KEY environment variable not set.")


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
    )


@app.post("/generate-signed-url/")
async def generate_signed_url(
    file_name: str, content_type: str, api_key: str = Depends(get_api_key)
):
    """
    Generates a signed URL for direct file upload to Google Cloud Storage.
    Requires API key authentication.
    """
    if not file_name or not content_type:
        raise HTTPException(
            status_code=400, detail="File name and content type are required."
        )

    # Basic validation for file_name to prevent path traversal
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name.")

    # Whitelist of allowed content types
    ALLOWED_CONTENT_TYPES = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/gif",
    ]
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported content type: {content_type}. "
                f"Allowed types are: {', '.join(ALLOWED_CONTENT_TYPES)}"
            ),
        )

    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_name)

        # Generate a V4 signed URL for uploading a file
        # The URL is valid for 15 minutes
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=3600,  # This URL will be valid for 1 hour
            method="PUT",
            content_type=content_type,
        )
        logger.info(
            f"Generated signed URL for {file_name} with content type "
            f"{content_type}"
        )
        return {"signed_url": signed_url, "file_name": file_name}

    except Exception as e:
        logger.error(f"Error generating signed URL: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {e}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
