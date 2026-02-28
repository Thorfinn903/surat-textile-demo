from .extensions import celery, cache
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery.task(bind=True, max_retries=3, name='tasks.process_image_task')
def process_image_task(self, product_id, filepath):
    logger.info(f"Task Started: optimizing image for Product {product_id}")
    try:
        from .utils.file_helpers import optimize_image
        from .models import Product
        from .extensions import db
        import os

        optimized_name = optimize_image(filepath)
        
        product = db.session.get(Product, product_id)
        if product:
            product.image_file = optimized_name
            db.session.commit()
            cache.clear()
            logger.info(f"Task Success: image optimized to {optimized_name} for Product {product_id}")
            return optimized_name
        else:
            logger.warning(f"Task Failure: Product {product_id} not found")
            return None
    except Exception as exc:
        logger.error(f"Task Failure: error optimizing image {filepath} - {exc}")
        raise self.retry(exc=exc, countdown=5)

@celery.task(name='tasks.generate_bulk_report')
def generate_bulk_report(user_id):
    """Dummy background task to simulate generating a PDF report."""
    print(f"Generating report for user {user_id}...")
    time.sleep(5)
    print(f"Report ready for user {user_id}.")
    return {"status": "completed", "url": "/static/reports/report_001.pdf"}
