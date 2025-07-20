from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, HTTPBearer
from google.cloud import storage
import os
from dotenv import load_dotenv
import logging
import firebase_admin
from firebase_admin import credentials, auth


# Load environment variables from .env file
load_dotenv()

app = FastAPI()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Firebase Admin SDK
# IMPORTANT: Download your service account key JSON file from Firebase Console
# Project settings -> Service accounts -> Generate new private key
# Place this file in the backend_api directory and ensure it's NOT committed to Git.
# Add it to your .gitignore: backend_api/serviceAccountKey.json
FIREBASE_SERVICE_ACCOUNT_KEY_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

if not os.path.exists(FIREBASE_SERVICE_ACCOUNT_KEY_PATH):
    logger.error(f"Firebase service account key not found at {FIREBASE_SERVICE_ACCOUNT_KEY_PATH}")
    raise FileNotFoundError("Firebase service account key file is missing.")

cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
firebase_admin.initialize_app(cred)


# Configure Google Cloud Storage
BUCKET_NAME = os.environ.get(
    "GCS_BUCKET_NAME", "ai-invoice-processor-0707-invoices"
)
storage_client = storage.Client()


# OAuth2 scheme for Firebase ID token
oauth2_scheme = HTTPBearer()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/generate-signed-url/")
async def generate_signed_url(
    file_name: str, content_type: str, current_user: dict = Depends(get_current_user)
):
    """
    Generates a signed URL for direct file upload to Google Cloud Storage.
    Requires Firebase authentication.
    """
    # You can access user info from current_user, e.g., current_user['uid']
    logger.info(f"User {current_user['uid']} requesting signed URL for {file_name}")

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
                f"Unsupported content type: {content_type}. Allowed types are: "
                f"{', '.join(ALLOWED_CONTENT_TYPES)}"
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