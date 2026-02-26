from flask import Blueprint, render_template, request, send_from_directory, current_app
from ...utils.constants import WORK_TYPE_OPTIONS, PRODUCT_CATEGORY_OPTIONS, MATERIAL_TYPE_OPTIONS
from ..catalog.services import get_filtered_products

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', 'All')
    work_type_filter = request.args.get('work_type', 'All')
    material_type_filter = request.args.get('material_type', 'All')
    sort_by = request.args.get('sort', 'newest')

    products = get_filtered_products(
        search_query=search_query,
        category=category_filter,
        work_type=work_type_filter,
        material_type=material_type_filter,
        sort_by=sort_by
    )

    return render_template('public/index.html', 
                          products=products,
                          work_type_options=WORK_TYPE_OPTIONS,
                          product_category_options=PRODUCT_CATEGORY_OPTIONS,
                          material_type_options=MATERIAL_TYPE_OPTIONS)

@public_bp.route('/about')
def about():
    return render_template('public/about.html')

@public_bp.route('/contact')
def contact():
    return render_template('public/contact.html')

@public_bp.route('/sw.js')
def service_worker():
    response = send_from_directory(current_app.static_folder, 'sw.js')
    response.headers['Cache-Control'] = 'no-cache'
    return response

@public_bp.route('/manifest.json')
def manifest():
    return send_from_directory(current_app.static_folder, 'manifest.json')
