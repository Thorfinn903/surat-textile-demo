from marshmallow import Schema, fields, validate

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    design_no = fields.Str(required=True)
    category = fields.Str(required=True)
    wholesale_price = fields.Float(required=True, validate=validate.Range(min=0))
    stock_status = fields.Str(validate=validate.OneOf(['AVAILABLE', 'SOLD OUT']))
    fabric = fields.Str()
    work_type = fields.Str()
    image_file = fields.Str(dump_only=True)
    views = fields.Int(dump_only=True)

class InquirySchema(Schema):
    product_id = fields.Int(required=True)
    visitor_name = fields.Str(required=True)
    phone_number = fields.Str(required=True)
    message = fields.Str()
