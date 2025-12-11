from marshmallow import Schema, fields, validates, ValidationError, validate

def validate_password(value):
    if not any(char.isdigit() for char in value):
        raise ValidationError('Password must include at least one number.')
    if not any(char.isalpha() for char in value):
        raise ValidationError('Password must include at least one letter.')
    if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in value):
        raise ValidationError('Password must include at least one special character.')

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True)

    master_password = fields.String(required=True, validate=[validate.Length(min=8, max=120), validate_password])

    class Meta:
        ordered = True

class SavedAccountSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    
    username = fields.String(required=False, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=False,)
    password = fields.String(required=False, validate=validate.Length(min=4, max=120))

    class Meta:
        ordered = True