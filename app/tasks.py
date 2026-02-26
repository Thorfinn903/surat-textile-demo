from .extensions import celery
import time

@celery.task(name='tasks.process_image_upload')
def process_image_upload(image_id):
    """Dummy background task to simulate image processing."""
    print(f"Started processing image {image_id}...")
    time.sleep(10) # Simulate heavy work
    print(f"Finished processing image {image_id}.")
    return True

@celery.task(name='tasks.generate_bulk_report')
def generate_bulk_report(user_id):
    """Dummy background task to simulate generating a PDF report."""
    print(f"Generating report for user {user_id}...")
    time.sleep(5)
    print(f"Report ready for user {user_id}.")
    return {"status": "completed", "url": "/static/reports/report_001.pdf"}
