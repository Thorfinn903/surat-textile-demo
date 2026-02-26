#!/bin/bash

# Exit on any error
set -e

echo "Starting Digital Dukan Backend..."

# Apply database migrations
echo "Applying migrations..."
export FLASK_APP=app.py
flask db upgrade || {
    echo "Migration failed, falling back to manual table creation (This is normal on first run if no migrations exist)"
    # This might happen if migration folder is not complete, 
    # but the app.__init__ call to db.create_all() will catch it
}

# Start the application
echo "Launching Gunicorn..."
gunicorn --config gunicorn_config.py app:app
