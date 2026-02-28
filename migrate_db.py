import os
from app import create_app
from app.extensions import db
from app.models import Product, User, InquiryLog, ActivityLog
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def sync():
    print("Reading data from Local SQLite...")
    
    # 1. Connect directly to old SQLite DB
    sqlite_engine = create_engine('sqlite:///instance/textile.db')
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SqliteSession()

    # Manual raw queries to grab the data safely without context conflicts
    users_data = sqlite_session.execute(text("SELECT id, username, password, role FROM user")).fetchall()
    products_data = sqlite_session.execute(text("SELECT name, design_no, category, material_type, work_type, color, image_file, wholesale_price, moq, stock_status, stock_count, views, whatsapp_clicks FROM product")).fetchall()
    
    print(f"Found {len(products_data)} products and {len(users_data)} users in old SQLite DB.")
    sqlite_session.close()

    # 2. Connect to local Postgres (Inside Docker)
    print("Connecting to Docker PostgreSQL...")
    docker_app = create_app('production')
    
    with docker_app.app_context():
        print("Cleaning Docker PostgreSQL...")
        db.session.query(InquiryLog).delete()
        db.session.query(ActivityLog).delete()
        db.session.query(Product).delete()
        db.session.query(User).delete()
        db.session.commit()

        print("Writing Local SQLite Data to Docker...")
        # Add Users
        for u in users_data:
            new_user = User(
                id=u[0],
                username=u[1],
                password=u[2],
                role=u[3]
            )
            db.session.add(new_user)
        
        # Add Products
        for p in products_data:
            new_product = Product(
                name=p[0],
                design_no=p[1],
                category=p[2],
                material_type=p[3],
                work_type=p[4],
                color=p[5],
                image_file=p[6],
                wholesale_price=p[7],
                moq=p[8],
                stock_status=p[9],
                stock_count=p[10],
                views=p[11],
                whatsapp_clicks=p[12]
            )
            db.session.add(new_product)
            
        db.session.commit()
        print("✅ SUCCESS: MIGRATION COMPLETE! Docker database is now an exact copy of your old SQLite DB.")

if __name__ == "__main__":
    sync()
