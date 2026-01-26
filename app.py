from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime, date
from PIL import Image
import os

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'surat-textile-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///textile.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)

# --- LOGIN MANAGER ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='client')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.String(20), default='In Stock')
    inquiry_count = db.Column(db.Integer, default=0)

class InquiryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    inquiry_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(100), nullable=False)  # Store username in case user is deleted
    activity_type = db.Column(db.String(50), nullable=False)  # 'stock_change', 'login', 'logout', 'user_deleted'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(100), nullable=True)  # Store product name in case product is deleted
    old_value = db.Column(db.String(100), nullable=True)  # Old stock status
    new_value = db.Column(db.String(100), nullable=True)  # New stock status
    activity_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    details = db.Column(db.Text, nullable=True)  # Additional details

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==========================================
# 🏠 CUSTOMER FACING ROUTES (Elite Hub)
# ==========================================

@app.route('/')
def index():
    # 1. Capture user inputs from the URL
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', 'All')
    work_type_filter = request.args.get('work_type', 'All')
    price_range_filter = request.args.get('price_range', 'All')
    
    # 2. Get all products from database
    products_query = Product.query.all()
    
    # 3. Step 2: Advanced Search Logic (D.No & Text)
    if search_query:
        try:
            # If search is a number, treat as D.No (1001, 1002...)
            design_no = int(search_query)
            target_id = design_no - 1000
            products = [p for p in products_query if p.id == target_id]
        except ValueError:
            # If text, search in name or category
            q = search_query.lower()
            products = [p for p in products_query if q in p.name.lower() or q in p.category.lower()]
    else:
        products = products_query

    # 4. Apply Category Pill Filter
    if category_filter != 'All':
        products = [p for p in products if p.category == category_filter]
    
    # 5. Apply Work Type Filter (search in name/category for keywords)
    if work_type_filter != 'All':
        work_keywords = {
            'Zari': ['zari', 'zardosi', 'gold'],
            'Embroidery': ['embroidery', 'embroid', 'handwork'],
            'Print': ['print', 'printed'],
            'Handwork': ['hand', 'handmade', 'handwork']
        }
        keywords = work_keywords.get(work_type_filter, [])
        if keywords:
            filtered = []
            for p in products:
                name_lower = p.name.lower()
                category_lower = p.category.lower()
                if any(kw in name_lower or kw in category_lower for kw in keywords):
                    filtered.append(p)
            products = filtered

    # 6. Apply Price Range Filter (placeholder - can be enhanced with actual price data)
    # For now, we'll use a simple heuristic based on category/name
    if price_range_filter != 'All':
        # This is a placeholder - can be enhanced when price data is available
        pass

    # Father's WhatsApp Number for all B2B Inquiry Buttons
    whatsapp_no = "919081653925" 
    return render_template('index.html', products=products, whatsapp_no=whatsapp_no)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/track-inquiry/<int:product_id>', methods=['POST'])
def track_inquiry(product_id):
    product = Product.query.get_or_404(product_id)
    product.inquiry_count += 1
    # Log inquiry timestamp
    inquiry_log = InquiryLog(product_id=product_id, inquiry_date=datetime.utcnow())
    db.session.add(inquiry_log)
    db.session.commit()
    return '', 204 # Silent success

# ==========================================
# 🔑 AUTHENTICATION ROUTES
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Log login activity
            activity = ActivityLog(
                user_id=user.id,
                username=user.username,
                activity_type='login',
                activity_date=datetime.utcnow(),
                details=f'User logged in from {request.remote_addr}'
            )
            db.session.add(activity)
            db.session.commit()
            return redirect(url_for('admin')) if user.role in ['admin', 'sales'] else redirect(url_for('index'))
        else:
            flash('Login Failed. Check details.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Log logout activity before logging out
    if current_user.is_authenticated:
        activity = ActivityLog(
            user_id=current_user.id,
            username=current_user.username,
            activity_type='logout',
            activity_date=datetime.utcnow(),
            details=f'User logged out from {request.remote_addr}'
        )
        db.session.add(activity)
        db.session.commit()
    logout_user()
    return redirect(url_for('index'))

# ==========================================
# 🛠️ ADMIN & SALES ROUTES (Step 6 Integrated)
# ==========================================

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role == 'client':
        return "Access Denied!"

    if request.method == 'POST':
        # Add New Product Logic
        if 'add_product' in request.form:
            name = request.form.get('name')
            category = request.form.get('category')
            file = request.files['image']
            
            if file:
                # Create a clean filename
                timestamp = db.session.query(Product).count() + 1
                filename = f"{name.replace(' ', '_')}_{timestamp}.webp"
                filepath = os.path.join('static/images', filename)
                
                # --- IMAGE OPTIMIZATION ENGINE ---
                img = Image.open(file)
                img = img.convert("RGB") # Ensure standard color mode
                
                # Resize logic: Set maximum width to 800px for fast loading
                if img.width > 800:
                    output_size = (800, int((800 / img.width) * img.height))
                    img = img.resize(output_size, Image.LANCZOS)
                    
                # Save as optimized WebP (Quality 80 is perfect for fabric detail)
                img.save(filepath, "WEBP", quality=80)
                
                # Save the optimized filename to the database
                new_product = Product(name=name, category=category, image=filename)
                db.session.add(new_product)
                db.session.commit()
                flash('Saree uploaded and automatically optimized for speed!')

            # Create New User Logic (Admin Only)
            elif 'create_user' in request.form:
                if current_user.role != 'admin':
                    return "Unauthorized action!"
                
                new_username = request.form.get('new_username')
                new_password = request.form.get('new_password')
                role = request.form.get('role')
            
            if User.query.filter_by(username=new_username).first():
                flash('Username exists!')
            else:
                hashed_pw = generate_password_hash(new_password, method='pbkdf2:sha256')
                new_user = User(username=new_username, password=hashed_pw, role=role)
                db.session.add(new_user)
                db.session.commit()
                flash(f'User created: {new_username}')

    products = Product.query.all()
    all_users = User.query.all() if current_user.role == 'admin' else []
    # Get recent activity logs (last 50)
    recent_activities = ActivityLog.query.order_by(ActivityLog.activity_date.desc()).limit(50).all() if current_user.role == 'admin' else []
    # Get top 10 trending products (by inquiry_count)
    trending_products = Product.query.order_by(Product.inquiry_count.desc()).limit(10).all()
    return render_template('admin.html', products=products, all_users=all_users, recent_activities=recent_activities, trending_products=trending_products)

# Step 6: One-Touch Stock Toggle Route
@app.route('/toggle-stock/<int:id>')
@login_required
def toggle_stock(id):
    if current_user.role == 'client': return "Denied"
    product = Product.query.get_or_404(id)
    old_stock = product.stock
    product.stock = 'Sold Out' if product.stock == 'In Stock' else 'In Stock'
    new_stock = product.stock
    
    # Log stock change activity
    activity = ActivityLog(
        user_id=current_user.id,
        username=current_user.username,
        activity_type='stock_change',
        product_id=product.id,
        product_name=product.name,
        old_value=old_stock,
        new_value=new_stock,
        activity_date=datetime.utcnow(),
        details=f'Stock changed for D.No: {product.id + 1000} from {old_stock} to {new_stock}'
    )
    db.session.add(activity)
    db.session.commit()
    flash(f"Status updated for D.No: {product.id + 1000}")
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if current_user.role != 'admin': return "Denied"
    product = Product.query.get_or_404(id)
    product_name = product.name
    product_dno = product.id + 1000
    db.session.delete(product)
    db.session.commit()
    flash(f'Product D.No: {product_dno} deleted successfully')
    return redirect(url_for('admin'))

@app.route('/delete-user/<int:id>')
@login_required
def delete_user(id):
    if current_user.role != 'admin': return "Access Denied!"
    if current_user.id == id:
        flash('You cannot delete your own account!')
        return redirect(url_for('admin'))
    
    user = User.query.get_or_404(id)
    username = user.username
    
    # Log user deletion activity
    activity = ActivityLog(
        user_id=current_user.id,
        username=current_user.username,
        activity_type='user_deleted',
        activity_date=datetime.utcnow(),
        details=f'User "{username}" (ID: {id}, Role: {user.role}) was deleted by {current_user.username}'
    )
    db.session.add(activity)
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" deleted successfully')
    return redirect(url_for('admin'))

# ==========================================
# 🛠️ SETUP & FIX ROUTES
# ==========================================

@app.route('/create-admin')
def create_admin():
    db.create_all()
    if User.query.filter_by(username='admin').first():
        return "Admin exists!"
    hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
    new_user = User(username='admin', password=hashed_password, role='admin')
    db.session.add(new_user)
    db.session.commit()
    return "Admin Setup Done! Login: admin / admin123"

@app.route('/update-db')
def update_db():
    with app.app_context():
        # This raw SQL command adds the missing column to your existing table
        db.session.execute(db.text('ALTER TABLE product ADD COLUMN inquiry_count INTEGER DEFAULT 0'))
        db.session.commit()
    return "Database updated with inquiry_count column!"

@app.route('/update-db-inquiry-log')
def update_db_inquiry_log():
    with app.app_context():
        db.create_all()
    return "InquiryLog table created!"

@app.route('/update-db-activity-log')
def update_db_activity_log():
    with app.app_context():
        db.create_all()
    return "ActivityLog table created!"

@app.route('/api/inquiry-count/<int:product_id>')
def get_today_inquiry_count(product_id):
    today = date.today()
    count = InquiryLog.query.filter(
        InquiryLog.product_id == product_id,
        db.func.date(InquiryLog.inquiry_date) == today
    ).count()
    return jsonify({'count': count})

@app.route('/api/trending')
def get_trending_products():
    # Get top 10 products by inquiry_count
    trending = Product.query.order_by(Product.inquiry_count.desc()).limit(10).all()
    products_data = [{
        'id': p.id,
        'name': p.name,
        'image': p.image,
        'category': p.category,
        'inquiry_count': p.inquiry_count,
        'stock': p.stock
    } for p in trending]
    return jsonify({'products': products_data})


# ==========================================
# 🏃 RUN SERVER
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)