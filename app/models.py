from datetime import datetime
from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    design_no = db.Column(db.String(50), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=True, index=True)
    material_type = db.Column(db.String(50), nullable=True)
    work_type = db.Column(db.String(50), nullable=True, index=True)
    color = db.Column(db.String(50), nullable=True)
    image_file = db.Column(db.String(100), nullable=False)
    wholesale_price = db.Column(db.Float, nullable=True)
    moq = db.Column(db.Integer, default=1)
    stock_status = db.Column(db.String(20), default='READY', index=True)
    stock_count = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    whatsapp_clicks = db.Column(db.Integer, default=0)
    
    @property
    def image(self):
        return self.image_file
        
    @image.setter
    def image(self, value):
        self.image_file = value

class InquiryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    inquiry_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(100), nullable=True)
    old_value = db.Column(db.String(100), nullable=True)
    new_value = db.Column(db.String(100), nullable=True)
    activity_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    details = db.Column(db.Text, nullable=True)
