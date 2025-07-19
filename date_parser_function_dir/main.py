import functions_framework
from datetime import datetime

@functions_framework.http
def parse_date(request):
    """
    Cloud Function to parse a date string and return it in YYYY-MM-DD format.
    Returns null if the date string is invalid.
    """
    request_json = request.get_json(silent=True)
    if request_json and 'date_string' in request_json:
        date_string = request_json['date_string']
    else:
        return {'parsed_date': None}, 400

    if not date_string:
        return {'parsed_date': None}, 200

    # Try common date formats
    formats = [
        "%Y-%m-%d", # YYYY-MM-DD
        "%m/%d/%Y", # MM/DD/YYYY
        "%d/%m/%Y", # DD/MM/YYYY
        "%Y/%m/%d", # YYYY/MM/DD
        "%b %d, %Y", # Jan 01, 2023
        "%B %d, %Y", # January 01, 2023
        "%d %b %Y", # 01 Jan 2023
        "%d %B %Y", # 01 January 2023
    ]

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt).strftime("%Y-%m-%d")
            return {'parsed_date': parsed_date}, 200
        except ValueError:
            continue

    # If no format matches, return None
    return {'parsed_date': None}, 200
