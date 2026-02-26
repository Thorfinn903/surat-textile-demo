from flask import current_app
from .utils.helpers import normalize_whatsapp_number
from .utils.constants import WORK_TYPE_OPTIONS, PRODUCT_CATEGORY_OPTIONS, ASSET_VERSION, DEFAULT_SETTINGS

def inject_global_template_data():
    shop = current_app.config.get('SHOP_SETTINGS', DEFAULT_SETTINGS)
    return {
        'shop_settings': shop,
        'whatsapp_no': normalize_whatsapp_number(shop.get('contact_number', '')),
        'work_type_options': WORK_TYPE_OPTIONS,
        'product_category_options': PRODUCT_CATEGORY_OPTIONS,
        'asset_version': ASSET_VERSION,
    }
