from datetime import datetime
import csv
import io
from sqlalchemy import func, text, inspect
from flask import current_app
from ...models import User, Product, ActivityLog, InquiryLog, db
from ...extensions import db, cache
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from ...utils.file_helpers import optimize_image


def get_admin_stats():
    total_skus = Product.query.count()
    sold_out_count = Product.query.filter(Product.stock_status == 'SOLD OUT').count()
    ready_stock_count = total_skus - sold_out_count
    return {
        'total_skus': total_skus,
        'sold_out_count': sold_out_count,
        'ready_stock_count': ready_stock_count
    }

def get_performance_analytics():
    def get_monthly_stats(group_by_col):
        return db.session.query(
            group_by_col,
            func.sum(Product.views).label('total_views'),
            func.sum(Product.whatsapp_clicks).label('total_clicks')
        ).group_by(group_by_col).order_by(
            (func.sum(Product.views)*1 + func.sum(Product.whatsapp_clicks)*5).desc()
        ).limit(5).all()

    def process_stats(stats_data):
        if not stats_data: return []
        _max = max([ (item.total_views + item.total_clicks*5) for item in stats_data ])
        max_score = _max if _max > 0 else 1
        results = []
        for item in stats_data:
            score = item.total_views + item.total_clicks * 5
            percent = (score / max_score) * 100
            results.append((item[0], score, percent))
        return results

    def get_inquiry_trends():
        from datetime import timedelta
        seven_days_ago = datetime.utcnow().date() - timedelta(days=6)
        
        # Query inquiries grouped by date
        trends = db.session.query(
            func.date(InquiryLog.inquiry_date).label('date'),
            func.count(InquiryLog.id).label('count')
        ).filter(InquiryLog.inquiry_date >= seven_days_ago
        ).group_by(func.date(InquiryLog.inquiry_date)
        ).order_by(func.date(InquiryLog.inquiry_date)).all()
        
        # Fill missing dates with 0
        trend_dict = {}
        for t in trends:
            # Handle both date objects and strings (SQLite returns strings for func.date)
            if isinstance(t.date, str):
                try:
                    d_obj = datetime.strptime(t.date, '%Y-%m-%d')
                    d_key = d_obj.strftime('%d %b')
                except:
                    d_key = t.date # Fallback
            else:
                d_key = t.date.strftime('%d %b')
            trend_dict[d_key] = t.count

        final_trends = []
        max_count = 0
        for i in range(7):
            day = (seven_days_ago + timedelta(days=i)).strftime('%d %b')
            count = trend_dict.get(day, 0)
            if count > max_count: max_count = count
            final_trends.append((day, count))
        return final_trends, max_count

    trends_data, max_val = get_inquiry_trends()

    return {
        'categories': process_stats(get_monthly_stats(Product.category)),
        'fabrics': process_stats(get_monthly_stats(Product.material_type)),
        'work_types': process_stats(get_monthly_stats(Product.work_type)),
        'inquiry_trends': trends_data,
        'max_inquiry': max_val if max_val > 0 else 1,
        'efficiency': db.session.query(
            Product.category,
            (func.sum(Product.whatsapp_clicks) * 1.0 / func.nullif(func.sum(Product.views), 0) * 100).label('conv_rate')
        ).group_by(Product.category).order_by(text('conv_rate DESC')).limit(3).all(),
        # Advanced Decision Logic
        'inventory_health': get_inventory_health_logic(),
        'dead_stock_count': Product.query.filter(Product.whatsapp_clicks == 0, Product.views > 10).count()
    }

def get_inventory_health_logic():
    total = Product.query.count()
    if total == 0: return 100
    
    # Active products = products with at least 1 inquiry or high views
    active = Product.query.filter((Product.whatsapp_clicks > 0) | (Product.views > 20)).count()
    health_percentage = (active / total) * 100
    
    status = "Excellent" if health_percentage > 80 else "Good" if health_percentage > 50 else "Critical"
    return {"percentage": round(health_percentage), "status": status}

def get_sorted_products(sort_by='newest', page=1, per_page=50):
    products_query = Product.query
    if sort_by == 'most_viewed':
        products_query = products_query.order_by(Product.views.desc(), Product.id.desc())
    elif sort_by == 'most_inquired':
        products_query = products_query.order_by(Product.whatsapp_clicks.desc(), Product.id.desc())
    elif sort_by == 'stock_out':
        products_query = products_query.filter(Product.stock_status == 'SOLD OUT').order_by(Product.id.desc())
    elif sort_by == 'dead_stock':
        products_query = products_query.filter(Product.whatsapp_clicks == 0, Product.views > 10).order_by(Product.views.desc())
    else:
        products_query = products_query.order_by(Product.id.desc())
        
    if page is None:
        return products_query.all()
        
    return products_query.paginate(page=page, per_page=per_page, error_out=False)

def get_all_users():
    return User.query.order_by(User.id.desc()).all()

def get_recent_activities(limit=50):
    return ActivityLog.query.order_by(ActivityLog.activity_date.desc()).limit(limit).all()

def add_product_service(form_data, image_file, user_id, username):
    name = form_data.get('name', '').strip()
    category = form_data.get('product_category', 'Saree')
    work_type = form_data.get('work_type', 'Print')
    material_type = form_data.get('material_type', 'Cotton')
    wholesale_price = float(form_data.get('wholesale_price', 0)) if form_data.get('wholesale_price') else None
    moq = int(form_data.get('moq', 4)) if form_data.get('moq') else 4

    if name and image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        upload_folder.mkdir(parents=True, exist_ok=True)
        save_path = upload_folder / filename
        image_file.save(str(save_path))

        new_product = Product(
            name=name,
            category=category,
            work_type=work_type,
            material_type=material_type,
            wholesale_price=wholesale_price,
            moq=moq,
            image_file=filename,
            stock_status='READY',
            design_no='AUTO'
        )
        db.session.add(new_product)
        db.session.flush() # To get the new_product.id

        from ...tasks import process_image_task
        process_image_task.delay(new_product.id, str(save_path))

        activity = ActivityLog(
            user_id=user_id,
            username=username,
            activity_type='add_product',
            activity_date=datetime.utcnow(),
            details=f'Added product: {name}'
        )
        db.session.add(activity)
        db.session.commit()
        
        # Invalidate cache
        cache.clear()
        
        return True, f'Product "{name}" added successfully! Image is being optimized.'
    return False, 'Please fill all fields and upload an image.'

def create_new_user(username, password, role, creator_id, creator_name):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    
    activity = ActivityLog(
        user_id=creator_id,
        username=creator_name,
        activity_type='create_user',
        activity_date=datetime.utcnow(),
        details=f'Created user: {username} ({role})'
    )
    db.session.add(activity)
    db.session.commit()
    return new_user

def toggle_product_stock(product_id, user_id, username):
    product = Product.query.get_or_404(product_id)
    old_stock = product.stock_status
    product.stock_status = 'SOLD OUT' if product.stock_status == 'READY' else 'READY'

    activity = ActivityLog(
        user_id=user_id,
        username=username,
        activity_type='stock_change',
        product_id=product.id,
        product_name=product.name,
        old_value=old_stock,
        new_value=product.stock_status,
        activity_date=datetime.utcnow(),
        details=f'Stock changed for D.No: {product.id + 1000} from {old_stock} to {product.stock_status}'
    )
    db.session.add(activity)
    db.session.commit()
    
    # Force clear cache so Trending/Analytics show updated status immediately
    cache.clear() 
    
    from ...extensions import socketio
    socketio.emit('stock_updated', {
        'product_id': product.id,
        'product_name': product.name,
        'new_status': product.stock_status,
        'message': f"Stock updated for {product.name} (D.No: {product.id + 1000}) to {product.stock_status}"
    }, to='admin_room')
    
    return product

def delete_product_service(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    cache.clear()
    return True

def delete_user_service(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return True

def process_bulk_upload_service(file):
    if not file or not file.filename.endswith('.csv'):
        return False, 'Invalid file format.'

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.DictReader(stream)
    count = 0
    for row in csv_input:
        new_product = Product(
            name=row.get('name', '').strip(),
            category=row.get('category', '').strip(),
            work_type=row.get('work_type', '').strip(),
            material_type=row.get('material_type', '').strip(),
            wholesale_price=float(row.get('wholesale_price', 0)) if row.get('wholesale_price') else None,
            moq=int(row.get('moq', 4)) if row.get('moq') else 4,
            image_file=row.get('image', 'default.jpg'),
            stock_status='READY'
        )
        db.session.add(new_product)
        count += 1
    db.session.commit()
    cache.clear()
    return True, f'Uploaded {count} products.'

def setup_initial_admin():
    if User.query.filter_by(username='admin').first():
        return False, 'Admin already exists.'
    hashed = generate_password_hash('admin123', method='pbkdf2:sha256')
    db.session.add(User(username='admin', password=hashed, role='admin'))
    db.session.commit()
    return True, 'Admin setup done! Login: admin / admin123'
