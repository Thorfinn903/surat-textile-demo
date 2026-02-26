from flask import Blueprint, render_template, request, session, jsonify
from ...utils.constants import WORK_TYPE_OPTIONS, PRODUCT_CATEGORY_OPTIONS, MATERIAL_TYPE_OPTIONS
from .services import (
    get_filtered_products, 
    track_product_inquiry, 
    track_product_view, 
    get_inquiry_count_for_product,
    get_serialized_trending_products
)

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/catalog')
def index():
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', 'All')
    work_type_filter = request.args.get('work_type', 'All')
    material_type_filter = request.args.get('material_type', 'All')
    sort_by = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    products = get_filtered_products(
        search_query=search_query,
        category=category_filter,
        work_type=work_type_filter,
        material_type=material_type_filter,
        sort_by=sort_by,
        page=page,
        per_page=per_page
    )

    return render_template('catalog/index.html',
                          products=products,
                          work_type_options=WORK_TYPE_OPTIONS,
                          product_category_options=PRODUCT_CATEGORY_OPTIONS,
                          material_type_options=MATERIAL_TYPE_OPTIONS)

@catalog_bp.route('/track-inquiry/<int:product_id>', methods=['POST'])
def track_inquiry(product_id):
    success, message = track_product_inquiry(product_id, session)
    if success:
        return '', 204
    return message, 200

@catalog_bp.route('/track-view/<int:product_id>', methods=['POST'])
def track_view(product_id):
    success, message = track_product_view(product_id, session)
    if success:
        return '', 204
    return message, 200

@catalog_bp.route('/api/inquiry-count/<int:product_id>')
def get_today_inquiry_count(product_id):
    count = get_inquiry_count_for_product(product_id)
    return jsonify({'count': count})

@catalog_bp.route('/api/trending')
def get_trending_products_api():
    products_data, mode = get_serialized_trending_products(limit=4)
    return jsonify({'products': products_data, 'mode': mode})
