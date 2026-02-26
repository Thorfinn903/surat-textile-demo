def set_secure_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Content Security Policy could be added here but needs careful configuration
    # response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

def register_middleware(app):
    @app.after_request
    def after_request(response):
        return set_secure_headers(response)
