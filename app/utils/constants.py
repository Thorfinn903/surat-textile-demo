from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEFAULT_SETTINGS = {
    'shop_name': 'Digital Dukan',
    'contact_number': '+91 90816 53925',
    'address': 'Shop No. 101, Millennium Market 2, Ring Road, Surat, Gujarat'
}

WORK_TYPE_OPTIONS = ['Embroidery', 'Print', 'Handwork']
PRODUCT_CATEGORY_OPTIONS = ['Saree', 'Kurti', 'Dress Material']
MATERIAL_TYPE_OPTIONS = ['Cotton', 'Silk', 'Polyester', 'Georgette', 'Chiffon', 'Rayon', 'Linen']
ASSET_VERSION = '8.0.0'

SETTINGS_PATH = BASE_DIR / 'settings.json'
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads' / 'products'
