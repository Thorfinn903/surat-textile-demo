from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from ...utils.constants import WORK_TYPE_OPTIONS, PRODUCT_CATEGORY_OPTIONS, MATERIAL_TYPE_OPTIONS
from ..catalog.services import get_trending_products
from ...models import User
from ...utils.auth import roles_required, admin_required
from .services import (
    get_admin_stats, 
    get_performance_analytics, 
    create_new_user, 
    toggle_product_stock,
    get_sorted_products,
    get_all_users,
    get_recent_activities,
    add_product_service,
    delete_product_service,
    delete_user_service,
    process_bulk_upload_service,
    setup_initial_admin
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'sales')
def admin():
    if request.method == 'POST':
        if 'add_product' in request.form:
            success, msg = add_product_service(request.form, request.files.get('image'), current_user.id, current_user.username)
            flash(msg)
            return redirect(url_for('admin.admin'))

        elif 'create_user' in request.form:
            # Only admin can create users
            if current_user.role != 'admin':
                flash('Only administrators can create users.')
                return redirect(url_for('admin.admin'))
                
            new_username = request.form.get('new_username', '').strip()
            new_password = request.form.get('new_password', '')
            role = request.form.get('role', 'sales')

            if new_username and new_password:
                if User.query.filter_by(username=new_username).first():
                    flash(f'Username "{new_username}" already exists.')
                else:
                    create_new_user(new_username, new_password, role, current_user.id, current_user.username)
                    flash(f'User "{new_username}" created successfully!')
            return redirect(url_for('admin.admin'))

    sort_by = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    products = get_sorted_products(sort_by, page=page, per_page=per_page)
    all_users = get_all_users() if current_user.role == 'admin' else []
    recent_activities = get_recent_activities() if current_user.role == 'admin' else []
    
    trending_products, trending_mode = get_trending_products(limit=4)
    stats = get_admin_stats()
    analytics = get_performance_analytics() if current_user.role == 'admin' else {'categories': [], 'fabrics': [], 'work_types': []}

    return render_template(
        'admin/index.html',
        products=products,
        total_skus=stats['total_skus'],
        ready_stock_count=stats['ready_stock_count'],
        sold_out_count=stats['sold_out_count'],
        all_users=all_users,
        recent_activities=recent_activities,
        trending_products=trending_products,
        trending_mode=trending_mode,
        work_type_options=WORK_TYPE_OPTIONS,
        product_category_options=PRODUCT_CATEGORY_OPTIONS,
        material_type_options=MATERIAL_TYPE_OPTIONS,
        analytics=analytics,
        top_categories=analytics['categories'],
        top_fabrics=analytics['fabrics'],
        top_work_types=analytics['work_types']
    )

@admin_bp.route('/toggle-stock/<int:id>')
@login_required
@roles_required('admin', 'sales')
def toggle_stock(id):
    product = toggle_product_stock(id, current_user.id, current_user.username)
    
    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax'):
        return {
            "status": "success",
            "new_status": product.stock_status,
            "message": f"Status updated to {product.stock_status}"
        }
        
    flash(f'Status updated for D.No: {id + 1000}')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    delete_product_service(id)
    flash(f'Product deleted')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/delete-user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    if current_user.id == id:
        flash('Cannot delete yourself!')
        return redirect(url_for('admin.admin'))
    delete_user_service(id)
    flash(f'User deleted')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/bulk-upload', methods=['POST'])
@login_required
@admin_required
def bulk_upload():
    success, msg = process_bulk_upload_service(request.files.get('file'))
    flash(msg)
    return redirect(url_for('admin.admin'))

@admin_bp.route('/create-admin')
def create_admin():
    # 1. Disable in production
    if current_app.config.get('ENV') == 'production':
        abort(404)
        
    # 2. Restrict to localhost or authenticated admin
    is_localhost = request.remote_addr in ('127.0.0.1', '::1')
    is_authenticated_admin = current_user.is_authenticated and current_user.role == 'admin'
    
    if not (is_localhost or is_authenticated_admin):
        abort(404)
        
    # 3. Allow only if no admin exists (unless already authenticated as admin)
    admin_exists = User.query.filter_by(role='admin').first() is not None
    if admin_exists and not is_authenticated_admin:
        abort(404)
        
    success, msg = setup_initial_admin()
    return msg
