from google.cloud import documentai_v1 as documentai
from google.api_core.exceptions import AlreadyExists, GoogleAPIError
import time

def create_processor(project_id: str, location: str, display_name: str, processor_type: str):
    """
    Creates a Document AI processor or retrieves an existing one.
    """
    client = documentai.DocumentProcessorServiceClient()
    parent = f"projects/{project_id}/locations/{location}"

    processor = documentai.Processor(
        display_name=display_name,
        type_=processor_type
    )

    try:
        print(f"Attempting to create processor: {display_name} ({processor_type}) in {location}...")
        # Attempt to create the processor
        operation = client.create_processor(parent=parent, processor=processor)
        # Wait for the operation to complete
        operation.result() 
        print(f"Processor creation operation completed.")

    except AlreadyExists:
        print(f"Processor '{display_name}' already exists. Proceeding to retrieve.")
    except GoogleAPIError as e:
        print(f"An API error occurred during creation: {e}")
        # If creation failed for another reason, we might not be able to retrieve it.
        return None
    except Exception as e:
        print(f"An unexpected error occurred during creation: {e}")
        return None

    # Always try to retrieve the processor after creation attempt or if it already exists
    print(f"Attempting to retrieve processor: {display_name}...")
    try:
        # List processors and find the one with the matching display_name and type.
        for p in client.list_processors(parent=parent):
            if p.display_name == display_name and p.type_ == processor_type:
                print(f"Found processor: {p.name}")
                return p
        print(f"Error: Processor '{display_name}' not found after creation attempt.")
        return None
    except Exception as e:
        print(f"An error occurred during retrieval: {e}")
        return None

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_documentai_processor.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    location = "us"
    display_name = "agency-invoice-parser"
    processor_type = "INVOICE_PROCESSOR"

    processor_info = create_processor(project_id, location, display_name, processor_type)

    if processor_info:
        processor_id_full = processor_info.name.split('/')[-1]
        print(f"Final Processor ID for '{display_name}': {processor_id_full}")
    else:
        print("Failed to create or retrieve Document AI processor.")

    print("\n--- Listing all available processors ---")
    try:
        client = documentai.DocumentProcessorServiceClient()
        parent = f"projects/{project_id}/locations/{location}"
        for p in client.list_processors(parent=parent):
            print(f"Processor Name: {p.display_name}, Type: {p.type_}, ID: {p.name.split('/')[-1]}, Full Name: {p.name}")
    except Exception as e:
        print(f"Error listing processors: {e}")