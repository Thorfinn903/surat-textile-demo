from ...models import Product, InquiryLog, db
from ...extensions import cache
from datetime import datetime, date

def get_filtered_products(search_query='', category='All', work_type='All', material_type='All', sort_by='newest', page=1, per_page=20):
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
                    Product.color.ilike(wildcard),
                    Product.design_no.ilike(wildcard)
                )
            )
            
    if category != 'All':
        products_query = products_query.filter(Product.category == category)

    if material_type != 'All':
         products_query = products_query.filter(Product.material_type == material_type)

    if work_type != 'All':
         products_query = products_query.filter(Product.work_type == work_type)

    if sort_by == 'trending':
        products_query = products_query.order_by(Product.views.desc(), Product.id.desc())
    elif sort_by == 'bestseller':
        products_query = products_query.order_by(Product.whatsapp_clicks.desc(), Product.id.desc())
    else: # newest
        products_query = products_query.order_by(Product.id.desc())

    if page is None:
        return products_query.all()
        
    return products_query.paginate(page=page, per_page=per_page, error_out=False)

def track_product_inquiry(product_id, session):
    product = Product.query.get_or_404(product_id)
    inquired_products = session.get('inquired_products', [])
    
    if product_id not in inquired_products:
        product.whatsapp_clicks = (product.whatsapp_clicks or 0) + 1
        inquired_products.append(product_id)
        session['inquired_products'] = inquired_products
        session.modified = True
        
        inquiry_log = InquiryLog(product_id=product_id, inquiry_date=datetime.utcnow())
        db.session.add(inquiry_log)
        db.session.commit()
        return True, "Tracked"
    return False, "Already Inquired"

def track_product_view(product_id, session):
    product = Product.query.get_or_404(product_id)
    viewed_products = session.get('viewed_products', [])
    
    if product_id not in viewed_products:
        product.views = (product.views or 0) + 1
        viewed_products.append(product_id)
        session['viewed_products'] = viewed_products
        session.modified = True
        db.session.commit()
        return True, "Tracked"
    return False, "Already Viewed"

@cache.memoize(timeout=300) # Cache for 5 minutes
def get_trending_products(limit: int = 4):
    products = Product.query.order_by(
        (Product.views * 1 + Product.whatsapp_clicks * 5).desc(),
        Product.id.desc()
    ).limit(limit).all()

    has_data = any((p.views or 0) > 0 or (p.whatsapp_clicks or 0) > 0 for p in products)
    mode = 'smart_score' if has_data else 'recently_added'
    
    return products, mode

def get_inquiry_count_for_product(product_id):
    today = date.today()
    return InquiryLog.query.filter(
        InquiryLog.product_id == product_id,
        db.func.date(InquiryLog.inquiry_date) == today
    ).count()

def get_serialized_trending_products(limit=4):
    trending, mode = get_trending_products(limit=limit)
    serialized = [{
        'id': p.id,
        'name': p.name,
        'image': p.image_file,
        'category': p.category,
        'work_type': p.work_type,
        'inquiry_count': p.whatsapp_clicks or 0,
        'view_count': p.views or 0,
        'stock': p.stock_status
    } for p in trending]
    return serialized, mode
