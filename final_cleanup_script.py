import os

file_to_delete = "C:/Users/dell7/Projects/AI_Agency_Project/delete_final_cleanup.py"

try:
    os.remove(file_to_delete)
    print(f"Successfully deleted {file_to_delete}")
except OSError as e:
    print(f"Error deleting {file_to_delete}: {e}")
