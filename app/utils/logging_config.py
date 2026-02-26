import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def configure_logging(app):
    # Disable default flask logging if needed
    # logging.getLogger('werkzeug').disabled = True
    
    log_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Stream handler (Stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)
    
    # File handler
    log_dir = Path(app.root_path).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / 'textile_demo.log', maxBytes=10240, backupCount=10
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(stream_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Digital Dukan Startup')
