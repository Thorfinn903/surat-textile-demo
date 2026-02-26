import random
from app.extensions import db
from app.models import User, Product
from werkzeug.security import generate_password_hash

def seed_database():
    """Seeds the database with an admin user and initial products if empty."""
    
    # 1. Check if Admin exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Creating default admin user...")
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
    
    # 2. Check if Products exist
    if Product.query.count() == 0:
        print("Database is empty. Seeding initial products...")
        
        categories = ['Saree', 'Kurti', 'Lehenga', 'Gown', 'Dress Material']
        fabrics = ['Silk', 'Cotton', 'Georgette', 'Chiffon', 'Linen', 'Rayon']
        works = ['Embroidery', 'Print', 'Handwork', 'Zari', 'Mirror Work']
        
        # Base realistic products
        for i in range(1, 51):
            category = random.choice(categories)
            fabric = random.choice(fabrics)
            work = random.choice(works)
            
            # Match actual Product model fields
            image_name = f"{fabric.lower()}_{work.lower()}_{category.lower().replace(' ', '_')}.jpg"
            
            p = Product(
                name=f"Premium {fabric} {category} with {work}",
                design_no=f"DS-{random.randint(1000, 9999)}",
                category=category,
                material_type=fabric,
                work_type=work,
                image_file=image_name,
                wholesale_price=random.randint(450, 4500),
                moq=random.choice([4, 8, 12, 16]),
                stock_status='AVAILABLE' if i > 5 else 'SOLD OUT',
                stock_count=random.randint(50, 500),
                views=random.randint(10, 100),
                whatsapp_clicks=random.randint(0, 10)
            )
            db.session.add(p)
            
        db.session.commit()
        print(f"✅ Seeding complete! Added {Product.query.count()} products.")
    else:
        print("Database already contains data. Skipping seeder.")
        db.session.commit()
