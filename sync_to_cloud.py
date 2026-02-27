import os
import sys
from sqlalchemy import create_all
from app import create_app
from app.extensions import db
from app.models import Product, User, InquiryLog, ActivityLog
from sqlalchemy import inspect

def sync():
    # 1. Create Local App Context to read SQLite
    local_app = create_app('development')
    
    print("Reading data from Local SQLite...")
    with local_app.app_context():
        local_products = Product.query.all()
        # Convert to list of dicts, removing internal state
        products_data = []
        for p in local_products:
            p_dict = {c.key: getattr(p, c.key) for c in inspect(p).mapper.column_attrs}
            # Remove ID to let Postgres auto-increment or keep it? 
            # Better to keep IDs if they are referenced elsewhere, but for now we'll let Postgres handle it
            if 'id' in p_dict: del p_dict['id']
            products_data.append(p_dict)
        
        local_users = User.query.all()
        users_data = []
        for u in local_users:
            u_dict = {c.key: getattr(u, c.key) for c in inspect(u).mapper.column_attrs}
            if 'id' in u_dict: u_dict.pop('id')
            users_data.append(u_dict)

    print(f"Found {len(products_data)} products and {len(users_data)} users in Local DB.")

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
        print("✅ SYNC COMPLETE! Cloud database is now an exact copy of your Local SQLite.")

if __name__ == "__main__":
    sync()
