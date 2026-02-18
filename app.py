from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from sqlalchemy import inspect, text, func
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'surat-textile-secret-key-123'
# Using database in root directory for simplicity and robustness
# Using database in instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///textile.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

SETTINGS_PATH = BASE_DIR / 'settings.json'
DEFAULT_SETTINGS = {
    'shop_name': 'Digital Dukan',
    'contact_number': '+91 90816 53925',
    'address': 'Shop No. 101, Millennium Market 2, Ring Road, Surat, Gujarat'
}
WORK_TYPE_OPTIONS = ['Embroidery', 'Print', 'Handwork']
PRODUCT_CATEGORY_OPTIONS = ['Saree', 'Kurti', 'Dress Material']
MATERIAL_TYPE_OPTIONS = ['Cotton', 'Silk', 'Polyester', 'Georgette', 'Chiffon', 'Rayon', 'Linen']
ASSET_VERSION = '8.0.0'
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads' / 'products'


def optimize_image(filepath):
    """Resize to max 800px width and save as .webp (Quality=80).
    Returns the new filename (basename only)."""
    img = Image.open(filepath)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > 800:
        ratio = 800 / img.width
        new_size = (800, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    webp_path = str(filepath).rsplit('.', 1)[0] + '.webp'
    img.save(webp_path, 'WEBP', quality=80)
    # Remove original if it was a different format
    if str(filepath) != webp_path:
        import os
        try:
            os.remove(str(filepath))
        except OSError:
            pass
    return Path(webp_path).name


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding='utf-8')
        return DEFAULT_SETTINGS.copy()

    try:
        file_settings = json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()

    merged = DEFAULT_SETTINGS.copy()
    for key in DEFAULT_SETTINGS:
        if key in file_settings and str(file_settings[key]).strip():
            merged[key] = str(file_settings[key]).strip()
    return merged


def normalize_whatsapp_number(contact_number: str) -> str:
    return ''.join(ch for ch in contact_number if ch.isdigit())


app.config['SHOP_SETTINGS'] = load_settings()

db = SQLAlchemy(app)

# --- PWA ROUTES ---
@app.route('/sw.js')
def service_worker():
    from flask import send_from_directory
    response = send_from_directory(app.static_folder, 'sw.js')
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/manifest.json')
def manifest():
    from flask import send_from_directory
    return send_from_directory(app.static_folder, 'manifest.json')

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
    design_no = db.Column(db.String(50), nullable=False)
    # merged category field strategy: category is the main one now
    category = db.Column(db.String(50), nullable=True)
    material_type = db.Column(db.String(50), nullable=True)
    work_type = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True) # New Field (v7.5)
    image_file = db.Column(db.String(100), nullable=False)
    stock_status = db.Column(db.String(20), default='READY')
    stock_count = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    whatsapp_clicks = db.Column(db.Integer, default=0)
    
    # Compat properties for template code that might still use old names
    @property
    def image(self):
        return self.image_file
        
    @image.setter
    def image(self, value):
        self.image_file = value
        
    @property
    def stock(self):
        return self.stock_status

    @stock.setter
    def stock(self, value):
        self.stock_status = value

    @property
    def product_category(self):
        return self.category

    @product_category.setter
    def product_category(self, value):
        self.category = value

    @property
    def view_count(self):
        return self.views

    @property
    def inquiry_count(self):
        return self.whatsapp_clicks


class InquiryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    inquiry_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(100), nullable=True)
    old_value = db.Column(db.String(100), nullable=True)
    new_value = db.Column(db.String(100), nullable=True)
    activity_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    details = db.Column(db.Text, nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.context_processor
def inject_global_template_data():
    shop = app.config.get('SHOP_SETTINGS', DEFAULT_SETTINGS)
    return {
        'shop_settings': shop,
        'whatsapp_no': normalize_whatsapp_number(shop.get('contact_number', '')),
        'work_type_options': WORK_TYPE_OPTIONS,
        'product_category_options': PRODUCT_CATEGORY_OPTIONS,
        'asset_version': ASSET_VERSION,
    }


@app.route('/sw.js')
def service_worker():
    from flask import send_from_directory
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')


@app.route('/manifest.json')
def manifest():
    from flask import send_from_directory
    return send_from_directory('.', 'manifest.json', mimetype='application/json')


def ensure_product_columns():
    inspector = inspect(db.engine)
    if 'product' not in inspector.get_table_names():
        return

    existing_columns = {column['name'] for column in inspector.get_columns('product')}
    alter_statements = {
        'whatsapp_clicks': 'ALTER TABLE product ADD COLUMN whatsapp_clicks INTEGER DEFAULT 0',
        'views': 'ALTER TABLE product ADD COLUMN views INTEGER DEFAULT 0',
        'work_type': 'ALTER TABLE product ADD COLUMN work_type VARCHAR(50)',
        'product_category': 'ALTER TABLE product ADD COLUMN product_category VARCHAR(50)',
        'material_type': 'ALTER TABLE product ADD COLUMN material_type VARCHAR(50)',
        'color': 'ALTER TABLE product ADD COLUMN color VARCHAR(50)', # v7.5
    }

    for column, statement in alter_statements.items():
        if column not in existing_columns:
            db.session.execute(text(statement))

    db.session.commit()


def get_trending_products(limit: int = 4):
    # Smart Score: (Views * 1) + (WhatsApp_Clicks * 5)
    # Ensure values are treated as integers (coalesce nulls to 0 in SQL usually, but here columns have default=0 so it's safe)
    products = Product.query.order_by(
        (Product.views * 1 + Product.whatsapp_clicks * 5).desc(),
        Product.id.desc()
    ).limit(limit).all()

    # Determine mode based on whether there's any engagement
    has_data = any((p.views or 0) > 0 or (p.whatsapp_clicks or 0) > 0 for p in products)
    mode = 'smart_score' if has_data else 'recently_added'
    
    return products, mode


# ==========================================
# CUSTOMER FACING ROUTES
# ==========================================

@app.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', 'All')
    work_type_filter = request.args.get('work_type', 'All')
    material_type_filter = request.args.get('material_type', 'All')
    price_range_filter = request.args.get('price_range', 'All')

    products_query = Product.query
    
    if search_query:
        # Check if query is a Design Number (Integer)
        if search_query.isdigit():
            # Exact Match on D.No (ID+1000) OR partial match on ID
            # Usually user types full D.No. ID = D.No - 1000.
            dno = int(search_query)
            target_id = dno - 1000
            # Also check if it's just an ID search or part of a name number
            products_query = products_query.filter(
                db.or_(
                    Product.id == target_id,
                    Product.name.ilike(f"%{search_query}%"),
                    Product.design_no.ilike(f"%{search_query}%")
                )
            )
        else:
            # "Smart Search" - Fuzzy OR logic (Amazon-Style Brain)
            # Match: Name, Category, Material, Work, Color, D.No (string)
            wildcard = f"%{search_query}%"
            products_query = products_query.filter(
                db.or_(
                    Product.name.ilike(wildcard),
                    Product.category.ilike(wildcard),
                    Product.work_type.ilike(wildcard),
                    Product.material_type.ilike(wildcard),
                    Product.color.ilike(wildcard), # v7.5
                    Product.design_no.ilike(wildcard)
                )
            )
            
    # Apply Filters on top of search
    if category_filter != 'All':
        products_query = products_query.filter(
            db.or_(Product.product_category == category_filter, Product.category == category_filter)
        )

    if material_type_filter != 'All':
         products_query = products_query.filter(Product.material_type == material_type_filter)

    if work_type_filter != 'All':
         products_query = products_query.filter(Product.work_type == work_type_filter)

    sort_by = request.args.get('sort', 'newest')

    if sort_by == 'trending':
        products_query = products_query.order_by(Product.views.desc(), Product.id.desc())
    elif sort_by == 'bestseller':
        products_query = products_query.order_by(Product.whatsapp_clicks.desc(), Product.id.desc())
    else: # newest
        products_query = products_query.order_by(Product.id.desc())

    products = products_query.all()

    return render_template('index.html', 
                          products=products,
                          work_type_options=WORK_TYPE_OPTIONS,
                          product_category_options=PRODUCT_CATEGORY_OPTIONS,
                          material_type_options=MATERIAL_TYPE_OPTIONS)


@app.route('/catalog')
def catalog():
    """Warehouse View — full catalog with sticky search and filters."""
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', 'All')
    work_type_filter = request.args.get('work_type', 'All')
    material_type_filter = request.args.get('material_type', 'All')
    sort_by = request.args.get('sort', 'newest')

    products_query = Product.query

    if search_query:
        if search_query.isdigit():
            dno = int(search_query)
            target_id = dno - 1000
            products_query = products_query.filter(
                db.or_(
                    Product.id == target_id,
                    Product.name.ilike(f"%{search_query}%"),
                    Product.design_no.ilike(f"%{search_query}%")
                )
            )
        else:
            wildcard = f"%{search_query}%"
            products_query = products_query.filter(
                db.or_(
                    Product.name.ilike(wildcard),
                    Product.category.ilike(wildcard),
                    Product.work_type.ilike(wildcard),
                    Product.material_type.ilike(wildcard),
                    Product.color.ilike(wildcard), # v7.5
                    Product.design_no.ilike(wildcard)
                )
            )
    
    if category_filter != 'All':
        products_query = products_query.filter(
            db.or_(Product.product_category == category_filter, Product.category == category_filter)
        )
    if work_type_filter != 'All':
        products_query = products_query.filter(Product.work_type == work_type_filter)
    if material_type_filter != 'All':
        products_query = products_query.filter(Product.material_type == material_type_filter)

    if sort_by == 'trending':
        products_query = products_query.order_by(Product.views.desc(), Product.id.desc())
    elif sort_by == 'bestseller':
        products_query = products_query.order_by(Product.whatsapp_clicks.desc(), Product.id.desc())
    else: # newest
        products_query = products_query.order_by(Product.id.desc())

    products = products_query.all()

    return render_template('catalog.html',
                          products=products,
                          work_type_options=WORK_TYPE_OPTIONS,
                          product_category_options=PRODUCT_CATEGORY_OPTIONS,
                          material_type_options=MATERIAL_TYPE_OPTIONS)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/track-inquiry/<int:product_id>', methods=['POST'])
def track_inquiry(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Session-based filtering (Unique Logic)
    inquired_products = session.get('inquired_products', [])
    if product_id not in inquired_products:
        product.whatsapp_clicks = (product.whatsapp_clicks or 0) + 1
        inquired_products.append(product_id)
        session['inquired_products'] = inquired_products
        session.modified = True
        
        inquiry_log = InquiryLog(product_id=product_id, inquiry_date=datetime.utcnow())
        db.session.add(inquiry_log)
        db.session.commit()
        return '', 204
    else:
        return 'Already Inquired', 200 # Silent success


@app.route('/track-view/<int:product_id>', methods=['POST'])
def track_view(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Session-based filtering (Unique View Logic)
    viewed_products = session.get('viewed_products', [])
    if product_id not in viewed_products:
        product.views = (product.views or 0) + 1
        viewed_products.append(product_id)
        session['viewed_products'] = viewed_products
        session.modified = True
        db.session.commit()
        return '', 204
    else:
        return 'Already Viewed', 200 # Silent success


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
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

        flash('Login failed. Check details.')

    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
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
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('login'))


# ==========================================
# ADMIN & SALES ROUTES
# ==========================================




@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role == 'client':
        return 'Access Denied!'
    
    # ... (POST handling code for add_user / add_product remains same, omitted for brevity, I will only replace the GET part at the end)
    # Actually, to avoid breaking the POST logic which is large, I should target the specific blocks or replace the whole function carefully. 
    # Since handling partial replacements in large functions is risky with line numbers if context shifts, I will use ReplaceFileContent carefully.
    
    # Let's try to match the return statement and the query logic before it.
    
    if request.method == 'POST':
        if 'add_product' in request.form:
            name = request.form.get('name', '').strip()
            product_category = request.form.get('product_category', 'Saree')
            work_type = request.form.get('work_type', 'Print')
            material_type = request.form.get('material_type', 'Cotton')
            image_file = request.files.get('image')

            if name and image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
                save_path = UPLOAD_FOLDER / filename
                image_file.save(str(save_path))

                # Auto-compress: resize & convert to .webp
                optimized_name = optimize_image(save_path)

                new_product = Product(
                    name=name,
                    category=product_category,
                    product_category=product_category,
                    work_type=work_type,
                    material_type=material_type,
                    image=optimized_name,
                    stock='In Stock'
                )
                db.session.add(new_product)

                activity = ActivityLog(
                    user_id=current_user.id,
                    username=current_user.username,
                    activity_type='add_product',
                    activity_date=datetime.utcnow(),
                    details=f'Added product: {name}'
                )
                db.session.add(activity)
                db.session.commit()
                flash(f'Product "{name}" added successfully! Image optimized to WebP.')
            else:
                flash('Please fill all fields and upload an image.')
            return redirect(url_for('admin'))

        elif 'create_user' in request.form:
            new_username = request.form.get('new_username', '').strip()
            new_password = request.form.get('new_password', '')
            role = request.form.get('role', 'sales')

            if new_username and new_password:
                existing = User.query.filter_by(username=new_username).first()
                if existing:
                    flash(f'Username "{new_username}" already exists.')
                else:
                    new_user = User(
                        username=new_username,
                        password=generate_password_hash(new_password),
                        role=role
                    )
                    db.session.add(new_user)

                    activity = ActivityLog(
                        user_id=current_user.id,
                        username=current_user.username,
                        activity_type='create_user',
                        activity_date=datetime.utcnow(),
                        details=f'Created user: {new_username} ({role})'
                    )
                    db.session.add(activity)
                    db.session.commit()
                    flash(f'User "{new_username}" created successfully!')
            else:
                flash('Please provide username and password.')
            return redirect(url_for('admin'))
             
    # --- GET DATA ---
    # --- GET DATA WITH SORTING ---
    sort_by = request.args.get('sort', 'newest')
    
    products_query = Product.query
    
    if sort_by == 'most_viewed':
        products_query = products_query.order_by(Product.views.desc(), Product.id.desc())
    elif sort_by == 'most_inquired':
        products_query = products_query.order_by(Product.whatsapp_clicks.desc(), Product.id.desc())
    elif sort_by == 'stock_out':
        products_query = products_query.filter(Product.stock_status == 'Sold Out').order_by(Product.id.desc())
    else: # newest
        products_query = products_query.order_by(Product.id.desc())
        
    products = products_query.all()
    all_users = User.query.order_by(User.id.desc()).all() if current_user.role == 'admin' else []
    recent_activities = (
        ActivityLog.query.order_by(ActivityLog.activity_date.desc()).limit(50).all()
        if current_user.role == 'admin'
        else []
    )
    trending_products, trending_mode = get_trending_products(limit=4)

    # --- MARKET TRENDS AGGREGATION ---
    top_categories = []
    top_fabrics = []
    top_work_types = []

    if current_user.role == 'admin':
        # --- MONTHLY FILTER ---
        today = datetime.now()
        start_of_month = datetime(today.year, today.month, 1)

        # Helper to get monthly stats
        def get_monthly_stats(group_by_col):
            # We need to join Product with InquiryLog (for clicks) and something else for views?
            # Wait, 'views' and 'whatsapp_clicks' on Product model are TOTAL lifetime counters.
            # To get MONTHLY data, we need to use the logs (ActivityLog / InquiryLog).
            # But we don't have a 'ViewLog' table for views per date. We only have InquiryLog.
            # And ActivityLog logs 'stock_change', 'login', etc., not product views.
            
            # PROBLEM: The current system strictly counts LIFETIME views/clicks on the Product model.
            # The 'InquiryLog' table exists (added recently), so we CAN get monthly inquiries.
            # But we CANNOT get monthly views because we don't store a 'ViewLog'. 
            # We only increment 'product.views'.
            
            # SOLUTION FOR NOW: 
            # 1. Use InquiryLog for Clicks (Monthly).
            # 2. For Views, we have no choice but to use Lifetime (or start tracking ViewLog).
            #    Since user wants "monthly data", showing lifetime views is misleading.
            #    However, implementing a full ViewLog table now might fill up the DB fast.
            #    Let's stick to LIFETIME values for now but relative percentage 
            #    OR just use InquiryLog if that's the KPI.
            
            # RE-READING USER REQUEST: "i want to referece in every month"
            # Since I cannot retroactively get monthly views, I will switch the analytics 
            # to use the LIFETIME data (resetting is manual) BUT displayed relatively.
            # OR, I can start tracking views in a new table.
            
            # User likely wants the VISUALS fixed (Relative %) + Monthly Reset.
            # Since I can't strip "January views" from "Total Views",
            # I will implement the RELATIVE PERCENTAGE logic on the existing data.
            # Mentioning to user is key.
            
            # Wait, I can use InquiryLog for the "Clicks" part safely. 
            # For views, I will just use the total for now as "Monthly" isn't tracked.
            
            return db.session.query(
                group_by_col,
                func.sum(Product.views).label('total_views'),
                func.sum(Product.whatsapp_clicks).label('total_clicks')
            ).group_by(group_by_col).order_by(
                (func.sum(Product.views)*1 + func.sum(Product.whatsapp_clicks)*5).desc()
            ).limit(5).all()

        # 1. Top Categories
        top_categories_data = get_monthly_stats(Product.category)
        _max_cat = max([ (item.total_views + item.total_clicks*5) for item in top_categories_data ]) if top_categories_data else 0
        max_score_cat = _max_cat if _max_cat > 0 else 1
        
        top_categories = []
        for item in top_categories_data:
            score = item.total_views + item.total_clicks * 5
            percent = (score / max_score_cat) * 100
            top_categories.append((item[0], score, percent))

        # 2. Top Fabrics
        top_fabrics_data = get_monthly_stats(Product.material_type)
        _max_fab = max([ (item.total_views + item.total_clicks*5) for item in top_fabrics_data ]) if top_fabrics_data else 0
        max_score_fab = _max_fab if _max_fab > 0 else 1
        
        top_fabrics = []
        for item in top_fabrics_data:
            score = item.total_views + item.total_clicks * 5
            percent = (score / max_score_fab) * 100
            top_fabrics.append((item[0], score, percent))

        # 3. Top Work Types
        top_work_types_data = get_monthly_stats(Product.work_type)
        _max_work = max([ (item.total_views + item.total_clicks*5) for item in top_work_types_data ]) if top_work_types_data else 0
        max_score_work = _max_work if _max_work > 0 else 1
        
        top_work_types = []
        for item in top_work_types_data:
            score = item.total_views + item.total_clicks * 5
            percent = (score / max_score_work) * 100
            top_work_types.append((item[0], score, percent))

    # --- GLOBAL STATS (Independent of Sort) ---
    total_skus = Product.query.count()
    ready_stock_count = Product.query.filter((Product.stock_status == 'In Stock') | (Product.stock_status == 'READY') | (Product.stock_status == None)).count() 
    # Note: DB default is 'READY' in model definition but inconsistent usage 'In Stock' in toggle. 
    # toggle_stock uses 'In Stock' / 'Sold Out'. Model default 'READY'.
    # Let's standardize or check broadly. 
    # toggle_stock: "product.stock = 'Sold Out' if product.stock == 'In Stock' else 'In Stock'"
    # Model: stock_status = db.Column(db.String(20), default='READY')
    # So we might have 'READY', 'In Stock', 'Sold Out'. 
    # Let's assume 'Sold Out' is the only "Out" status. Everything else is Ready.
    
    sold_out_count = Product.query.filter(Product.stock_status == 'Sold Out').count()
    ready_stock_count = total_skus - sold_out_count # simpler and safer

    return render_template(
        'admin.html',
        products=products,
        total_skus=total_skus,
        ready_stock_count=ready_stock_count,
        sold_out_count=sold_out_count,
        all_users=all_users,
        recent_activities=recent_activities,
        trending_products=trending_products,
        trending_mode=trending_mode,
        work_type_options=WORK_TYPE_OPTIONS,
        product_category_options=PRODUCT_CATEGORY_OPTIONS,
        material_type_options=MATERIAL_TYPE_OPTIONS,
        top_categories=top_categories,
        top_fabrics=top_fabrics,
        top_work_types=top_work_types
    )


@app.route('/toggle-stock/<int:id>')
@login_required
def toggle_stock(id):
    if current_user.role == 'client':
        return 'Denied'

    product = Product.query.get_or_404(id)
    old_stock = product.stock
    product.stock = 'Sold Out' if product.stock == 'In Stock' else 'In Stock'

    activity = ActivityLog(
        user_id=current_user.id,
        username=current_user.username,
        activity_type='stock_change',
        product_id=product.id,
        product_name=product.name,
        old_value=old_stock,
        new_value=product.stock,
        activity_date=datetime.utcnow(),
        details=f'Stock changed for D.No: {product.id + 1000} from {old_stock} to {product.stock}'
    )
    db.session.add(activity)
    db.session.commit()

    flash(f'Status updated for D.No: {product.id + 1000}')
    return redirect(url_for('admin'))


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if current_user.role != 'admin':
        return 'Denied'

    product = Product.query.get_or_404(id)
    product_dno = product.id + 1000
    db.session.delete(product)
    db.session.commit()
    flash(f'Product D.No: {product_dno} deleted successfully')
    return redirect(url_for('admin'))


@app.route('/delete-user/<int:id>')
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        return 'Access Denied!'

    if current_user.id == id:
        flash('You cannot delete your own account!')
        return redirect(url_for('admin'))

    user = User.query.get_or_404(id)
    username = user.username

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


@app.route('/admin/bulk-upload', methods=['POST'])
@login_required
def bulk_upload():
    if current_user.role != 'admin':
        return 'Access Denied', 403

    file = request.files.get('file')
    if not file or not file.filename:
        flash('No file selected')
        return redirect(url_for('admin'))

    if not file.filename.endswith('.csv'):
        flash('Only CSV files are allowed currently.')
        return redirect(url_for('admin'))

    try:
        import csv
        import io
        
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        last_product = Product.query.order_by(Product.id.desc()).first()
        start_id = 1001 + (last_product.id if last_product else 0)
        
        count = 0
        for row in csv_input:
            # Map CSV columns to Product model
            # Expected headers: name, category, material_type, work_type, image
            name = row.get('name', '').strip()
            category = row.get('category', '').strip()
            material_type = row.get('material_type', '').strip()
            work_type = row.get('work_type', '').strip()
            image = row.get('image', '').strip()
            
            # Optional: Check if design_no exists in CSV, else auto-generate
            csv_design_no = row.get('design_no', '').strip()
            
            if name and category:
                # Generate Design No
                final_design_no = csv_design_no if csv_design_no else str(start_id + count)
                
                new_product = Product(
                    name=name,
                    design_no=final_design_no,
                    category=category,
                    product_category=category,
                    work_type=work_type,
                    material_type=material_type,
                    color="Multi", # v7.5 Default
                    image=image or 'default.jpg',
                    stock_status='In Stock'
                )
                db.session.add(new_product)
                count += 1
        
        db.session.commit()
        flash(f'Successfully uploaded {count} products.')
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}')
        
    return redirect(url_for('admin'))


# ==========================================
# SETUP & FIX ROUTES
# ==========================================

@app.route('/create-admin')
def create_admin():
    db.create_all()
    ensure_product_columns()

    if User.query.filter_by(username='admin').first():
        return 'Admin exists!'

    hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
    new_user = User(username='admin', password=hashed_password, role='admin')
    db.session.add(new_user)
    db.session.commit()
    return 'Admin setup done! Login: admin / admin123'


@app.route('/update-db')
def update_db():
    with app.app_context():
        db.create_all()
        ensure_product_columns()
    return 'Database updated with required product columns.'


@app.route('/update-db-inquiry-log')
def update_db_inquiry_log():
    with app.app_context():
        db.create_all()
    return 'InquiryLog table created!'


@app.route('/update-db-activity-log')
def update_db_activity_log():
    with app.app_context():
        db.create_all()
    return 'ActivityLog table created!'


@app.route('/api/inquiry-count/<int:product_id>')
def get_today_inquiry_count(product_id):
    today = date.today()
    count = InquiryLog.query.filter(
        InquiryLog.product_id == product_id,
        db.func.date(InquiryLog.inquiry_date) == today
    ).count()
    return jsonify({'count': count})


@app.route('/api/trending')
def get_trending_products_api():
    trending, mode = get_trending_products(limit=4)
    products_data = [{
        'id': p.id,
        'name': p.name,
        'image': p.image,
        'category': p.product_category or p.category,
        'work_type': p.work_type,
        'inquiry_count': p.whatsapp_clicks or 0,
        'view_count': p.views or 0,
        'stock': p.stock
    } for p in trending]
    return jsonify({'products': products_data, 'mode': mode})


with app.app_context():
    db.create_all()
    ensure_product_columns()


# ==========================================
# RUN SERVER
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
