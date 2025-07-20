import functions_framework
from dateutil.parser import parse
import flask


@functions_framework.http
def date_parser_helper(request: flask.Request):
    """
    An HTTP-triggered Cloud Function to parse date strings.
    """
    request_json = request.get_json(silent=True)

    if not request_json or 'date_string' not in request_json:
        return flask.jsonify(
            {"error": "Invalid request. 'date_string' is required."}
        ), 400

    date_string = request_json['date_string']

    if not date_string:
        return flask.jsonify({"parsed_date": None})

    try:
        parsed_date = parse(date_string)
        return flask.jsonify({"parsed_date": parsed_date.strftime('%Y-%m-%d')})
    except (ValueError, TypeError):
        return flask.jsonify({"parsed_date": None})
