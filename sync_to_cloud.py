import os
import sys
from app import create_app
from app.extensions import db
from app.models import Product, User, InquiryLog, ActivityLog
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def sync():
    # 1. Create Local App Context to read SQLite
    print("Reading data from Local SQLite...")
    
    # Connect directly to old SQLite DB
    sqlite_engine = create_engine('sqlite:///instance/textile.db')
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SqliteSession()

    # Manual raw queries to grab the data safely without context conflicts
    users_data_raw = sqlite_session.execute(text("SELECT id, username, password, role FROM user")).fetchall()
    products_data_raw = sqlite_session.execute(text("SELECT name, design_no, category, material_type, work_type, color, image_file, wholesale_price, moq, stock_status, stock_count, views, whatsapp_clicks FROM product")).fetchall()
    
    users_data = []
    for u in users_data_raw:
        users_data.append({
            'id': u[0], 'username': u[1], 'password': u[2], 'role': u[3]
        })
        
    products_data = []
    for p in products_data_raw:
        products_data.append({
            'name': p[0], 'design_no': p[1], 'category': p[2], 'material_type': p[3], 
            'work_type': p[4], 'color': p[5], 'image_file': p[6], 'wholesale_price': p[7], 
            'moq': p[8], 'stock_status': p[9], 'stock_count': p[10], 'views': p[11], 
            'whatsapp_clicks': p[12]
        })

    print(f"Found {len(products_data)} products and {len(users_data)} users in Local DB.")
    sqlite_session.close()

    # 2. Connect to Cloud Postgres
    cloud_url = os.environ.get('RENDER_POSTGRES_URL')
    if not cloud_url:
        print("❌ Error: RENDER_POSTGRES_URL environment variable is not set!")
        print("Setup: Get 'External Database URL' from Render Postgres Dashboard and set it locally.")
        return

    # Fix postgres prefix for SQLAlchemy if needed
    if cloud_url.startswith("postgres://"):
        cloud_url = cloud_url.replace("postgres://", "postgresql://", 1)

    print("Connecting to Cloud Database...")
    cloud_app = create_app('production')
    cloud_app.config['SQLALCHEMY_DATABASE_URI'] = cloud_url
    
    with cloud_app.app_context():
        print("Cleaning Cloud Data...")
        # Delete existing ulat-pulat data
        db.session.query(InquiryLog).delete()
        db.session.query(ActivityLog).delete()
        db.session.query(Product).delete()
        db.session.query(User).delete()
        db.session.commit()

        print("Writing Local Data to Cloud...")
        # Re-add Users
        for u_data in users_data:
            db.session.add(User(**u_data))
        
        # Re-add Products
        for p_data in products_data:
            db.session.add(Product(**p_data))
        
        db.session.commit()
        print("SUCCESS: SYNC COMPLETE! Cloud database is now an exact copy of your Local SQLite.")

if __name__ == "__main__":
    sync()
