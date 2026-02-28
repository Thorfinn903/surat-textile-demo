from flask import Blueprint, jsonify, request, g
from ....utils.responses import success_response, error_response
from ....models import Product, User, InquiryLog, db
from ....utils.jwt_auth import token_required, generate_tokens
from werkzeug.security import check_password_hash
import jwt
from flask import current_app
from sqlalchemy import func
from ....schemas import ProductSchema
from ....extensions import limiter

api_v1_bp = Blueprint('api_v1', __name__)

@api_v1_bp.route('/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate and get JWT tokens."""
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return error_response(message="Missing username or password", status_code=400)
    
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        tokens = generate_tokens(user.id, user.role)
        return success_response(data=tokens, message="Successfully authenticated")
    
    return error_response(message="Invalid credentials", status_code=401)

@api_v1_bp.route('/auth/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token."""
    data = request.json
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return error_response(message="Missing refresh token", status_code=400)
        
    try:
        payload = jwt.decode(refresh_token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            return error_response(message="Invalid token type", status_code=401)
            
        user = db.session.get(User, payload['sub'])
        if not user:
            return error_response(message="User not found", status_code=401)
            
        tokens = generate_tokens(user.id, user.role)
        return success_response(data=tokens, message="Token refreshed successfully")
        
    except jwt.ExpiredSignatureError:
        return error_response(message="Refresh token expired. Please log in again.", status_code=401)
    except jwt.InvalidTokenError:
        return error_response(message="Invalid refresh token.", status_code=401)

@api_v1_bp.route('/ping', methods=['GET'])
def ping():
    """Simple health check endpoint."""
    return success_response(message="API v1 is operational")

@api_v1_bp.route('/products', methods=['GET'])
@token_required()
def get_products():
    """
    Paginated list of products.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        products_pagination = Product.query.order_by(Product.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        data = {
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "design_no": p.design_no,
                    "category": p.category,
                    "wholesale_price": p.wholesale_price,
                    "stock_status": p.stock_status,
                    "image_url": f"/static/images/{p.image_file}"
                } for p in products_pagination.items
            ],
            "meta": {
                "page": products_pagination.page,
                "per_page": per_page,
                "total_pages": products_pagination.pages,
                "total_items": products_pagination.total
            }
        }
        return success_response(data=data)
    except Exception as e:
        return error_response(message=str(e), status_code=500)

@api_v1_bp.route('/products', methods=['POST'])
@token_required(roles=['admin', 'sales'])
@limiter.limit("5 per minute")
def create_product():
    """
    Create a new product.
    """
    schema = ProductSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response(message="Validation failed", errors=errors, status_code=400)
    
    try:
        data = request.json
        new_product = Product(
            name=data['name'],
            design_no=data['design_no'],
            category=data['category'],
            wholesale_price=data['wholesale_price'],
            material_type=data.get('fabric', ''),
            work_type=data.get('work_type', ''),
            stock_status=data.get('stock_status', 'AVAILABLE'),
            image_file='default.jpg'  # Placeholder for demo
        )
        db.session.add(new_product)
        db.session.flush() # flush to get ID
        
        # Dispatch Celery processing if needed (Assuming fake file logic here)
        db.session.commit()
        return success_response(data=schema.dump(new_product), status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(message="Failed to create product", errors=[str(e)])

@api_v1_bp.route('/dashboard-stats', methods=['GET'])
@token_required(roles=['admin', 'sales'])
def dashboard_stats():
    """
    Returns high-level business metrics for the B2B dashboard.
    """
    try:
        total_products = Product.query.count()
        total_inquiries = InquiryLog.query.count()
        total_views = db.session.query(func.sum(Product.views)).scalar() or 0
        out_of_stock = Product.query.filter(Product.stock_status == 'SOLD OUT').count()
        
        data = {
            "inventory_summary": {
                "total_items": total_products,
                "active_items": total_products - out_of_stock,
                "out_of_stock_count": out_of_stock
            },
            "engagement_metrics": {
                "total_whatsapp_inquiries": total_inquiries,
                "total_web_views": int(total_views),
                "conversion_rate": round((total_inquiries / total_views * 100), 2) if total_views > 0 else 0
            }
        }
        return success_response(data=data)
    except Exception as e:
        return error_response(message="Failed to aggregate stats", errors=[str(e)])

@api_v1_bp.route('/admin/users', methods=['GET'])
@token_required(roles=['admin'])
def get_admin_users():
    """
    List all system users. 
    Requires Bearer Token in Authorization header and Admin role.
    """
    try:
        users = User.query.all()
        data = [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role
            } for u in users
        ]
        return success_response(data=data)
    except Exception as e:
        return error_response(message="Internal processing error", status_code=500)
