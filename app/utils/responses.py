from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """
    Standard success response helper.
    """
    response = {
        "status": "success",
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(message="An error occurred", status_code=400, errors=None):
    """
    Standard error response helper.
    """
    response = {
        "status": "error",
        "message": message
    }
    if errors is not None:
        response["errors"] = errors
    return jsonify(response), status_code
