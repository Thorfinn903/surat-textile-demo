from flask import Flask, render_template, request, redirect, url_for, session

from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_surat'
# --- CONFIGURATION ---
# 1. Database Setup (Ye data ko permanent karega)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///textile.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Upload Folder
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database Initialize
db = SQLAlchemy(app)

# --- DATABASE MODEL (Table ka naksha) ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.String(20), default='In Stock')

# App start hone se pehle database banao
with app.app_context():
    db.create_all()

# --- ROUTES (Pages) ---

# app.py mein jahan @app.route('/') hai, wahan ye pura replace kar de:

@app.route('/')
def index():
    # 1. User ne kya search kiya? (Query uthao)
    search_query = request.args.get('q')
    category_filter = request.args.get('category')

    # 2. Database se saare products le aao
    filtered_products = Product.query.all()

    # 3. Agar search box mein kuch likha hai, to filter lagao
    if search_query:
        # Lowercase isliye kiya taaki 'RED' aur 'red' dono pakad le
        filtered_products = [p for p in filtered_products if search_query.lower() in p.name.lower()]
    
    # 4. Agar category select ki hai (aur 'All' nahi hai), to filter lagao
    if category_filter and category_filter != 'All':
        filtered_products = [p for p in filtered_products if p.category == category_filter]

    # 5. Filter kiya hua maal hi HTML ko bhejo
    return render_template('index.html', products=filtered_products)

@app.route('/about')
def about():
    return render_template('about.html', title="About Us - Surat Textile Hub")

@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact Us - Bulk Orders")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # 1. SECURITY CHECK (Sabse pehle check karo login hai ya nahi)
    if 'user' not in session:
        return redirect(url_for('login'))
        
    # 2. AGAR KOI PHOTO UPLOAD KAR RAHA HAI (POST)
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        photo = request.files['image']
        
        if photo:
            filename = photo.filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Database me add karna
            new_product = Product(name=name, category=category, image=filename)
            db.session.add(new_product)
            db.session.commit()
            
        return redirect(url_for('admin'))

    # 3. AGAR BAS PAGE KHOLNA HAI (GET) 
    # (Ye lines 'if' ke bahar, deewar se satakar honi chahiye)
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/toggle_stock/<int:id>')
def toggle_stock(id):
    product = Product.query.get_or_404(id)
    if product.stock == 'In Stock':
        product.stock = 'Sold Out'
    else:
        product.stock = 'In Stock'
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Yahan apna User/Pass set kar lo
        if username == 'admin' and password == 'admin123':
            session['user'] = 'sales_team' # Session shuru
            return redirect(url_for('admin'))
        else:
            return "Galat Password! Wapis try karo."
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None) # Session khatam
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)