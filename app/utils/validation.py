from flask import request, abort

def validate_json_request(required_fields):
    data = request.get_json()
    if not data:
        abort(400, description="Missing JSON data")
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing required field: {field}")
    return data

def validate_form_request(required_fields):
    for field in required_fields:
        if field not in request.form:
            abort(400, description=f"Missing required field: {field}")
    return request.form
