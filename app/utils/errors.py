from flask import render_template, request
from .responses import error_response

def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith('/api/'):
            return error_response(message="Resource not found", status_code=404)
        return render_template('public/index.html'), 404 # Or a 404 page if available

    @app.errorhandler(403)
    def handle_403(e):
        if request.path.startswith('/api/'):
            return error_response(message="Forbidden access", status_code=403)
        return "Forbidden", 403

    @app.errorhandler(429)
    def handle_429(e):
        if request.path.startswith('/api/'):
            return error_response(message="Too many requests", status_code=429)
        return "Rate limit exceeded", 429

    @app.errorhandler(500)
    def handle_500(e):
        if request.path.startswith('/api/'):
            return error_response(message="An unexpected server error occurred", status_code=500)
        return render_template('public/index.html'), 500
