from marshmallow import fields, ValidationError, post_load, pre_load, validate, Schema, validates
from ..models import User, Cart

class UserSchema(Schema):
    
    id = fields.Integer()
    username = fields.String(required=True, validate=validate.Length(min=4, max=20))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8))
    joined_at = fields.DateTime(dump_only=True) 


    @validates("email")
    def validate_email(self, email, **kwargs):
        usr = User.get_user_by_email(email)

        if usr:
            raise ValidationError("Email already exists asdas")

    @validates("username")
    def validate_username(self, username, **kwargs):
        usr = User.get_user_by_username(username)
        if usr:
            raise ValidationError("Username already exists")

    @validates("password")
    def validate_password(self, password, **kwargs):

        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one digit")
        
        if any(char.isupper() for char in password) is False:
            raise ValidationError("Password must contain at least one uppercase letter")
        
        if any(char.islower() for char in password) is False:
            raise ValidationError("Password must contain at least one lowercase letter")
        
        if any(char in "!@#$%^&*()_+-=" for char in password) is False:
            raise ValidationError("Password must contain at least one special character")


    @post_load
    def make_user(self, data, **kwargs):
        usr = User(**data)
        usr.save()
        # Create a cart for the user
        usr.cart = Cart(user_id=usr.id)
        usr.cart.save()

        return usr
