import random
import os
from app.extensions import db
from app.models import User, Product
from werkzeug.security import generate_password_hash

def seed_database(force=False):
    """Seeds the database using ONLY actual images present in the folder."""
    
    if force:
        print("FORCING RESET: Cleaning all data...")
        Product.query.delete()
        User.query.delete()
        db.session.commit()

    # 1. Create Admin
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
    
    # 2. Seed Products only if empty
    if Product.query.count() == 0:
        print("Seeding from local assets...")
        image_dir = os.path.join('static', 'images')
        # Get actual filenames like 'cotton_print_saree.jpg'
        all_images = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.webp', '.avif'))]
        
        for img in all_images:
            if '_' not in img: continue # Skip banners
            
            # Extract info from filename: fabric_work_category.jpg
            parts = img.split('.')[0].split('_')
            if len(parts) >= 3:
                fabric = parts[0].capitalize()
                work = parts[1].capitalize()
                category = " ".join(parts[2:]).capitalize()
                
                p = Product(
                    name=f"Premium {fabric} {category} ({work})",
                    design_no=f"DN-{random.randint(1000, 9999)}",
                    category=category,
                    material_type=fabric,
                    work_type=work,
                    image_file=img,
                    wholesale_price=random.randint(400, 2500),
                    moq=random.choice([4, 8, 12]),
                    stock_status='READY',
                    stock_count=random.randint(100, 1000),
                    views=random.randint(5, 50),
                    whatsapp_clicks=random.randint(0, 5)
                )
                db.session.add(p)
        
        db.session.commit()
        print(f"✅ Restart Successful! Loaded {Product.query.count()} products from real images.")
