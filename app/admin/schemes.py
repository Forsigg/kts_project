from marshmallow import Schema, fields


class AdminSchema(Schema):
    id = fields.Int(required=True)
    email = fields.Str(required=True)


class AdminValidationSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)
