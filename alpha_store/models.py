from flask_sqlalchemy import SQLAlchemy
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from typing import Union, Optional
from datetime import datetime

# db and login manager are initialized here, but they will be configured in the configure function.
# With this, we can use both without import ``app`` instance, avoiding circular imports
# Also, since our application have only simple models, i will use the same models.py to configure products and user models.

db = SQLAlchemy()
login_manager = LoginManager()


def configure(app: flask.Flask) -> None:
    """
    Set up database and login manager for auth package
    """

    # We will check if the app is running in test mode or not, and provide the correct database URI
    # With this, i dont need to use differents session for testing and development
    if app.testing:
        try:
            db_credentials = app.config["cfg"]["MOCK_DATABASE"]
        except (KeyError, ValueError) as exc:
            app.logger.error(
                f"Error while trying to get mock database credentials: {exc}")
            raise exc
    else:
        try:
            db_credentials = app.config["cfg"]["DATABASE"]

        except (KeyError, ValueError) as exc:
            app.logger.error(
                f"Error while trying to get the main database credentials: {exc}")
            raise exc

    # Set database URI
    db_uri = f"postgresql+pg8000://{db_credentials['db_user']}:{db_credentials['db_pass']}@{db_credentials['db_host']}/{db_credentials['db_name']}"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.db = db

    app.logger.info(
        f"Connected in {db_credentials['db_name']} with app testing status: {app.testing}")
    app.logger.debug(
        f"Database URI: {app.db}, {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Set up login manager
    login_manager.init_app(app)
    app.login_menager = login_manager

    app.logger.info("Auth models configured")


@login_manager.user_loader
def load_user(user_id: Union[int, str]) -> Optional["User"]:
    return User.query.get(int(user_id))


# Association table for many to many relationship
cart_products_association = db.Table(
    'cart_product', db.Model.metadata,
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'))
)


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True,
                         unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    joined_at = db.Column(db.DateTime, default=db.func.now())

    # One to one relationship with cart
    cart = db.relationship("Cart", backref="user", uselist=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Hash password on user creation
        self.hash_password()

    def hash_password(self) -> None:
        self.password = generate_password_hash(self.password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f"<User username={self.username}, email={self.email}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "joined_at": self.joined_at
        }

    @classmethod
    def get_user_by_email(cls, email: str) -> Optional["User"]:
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_user_by_username(cls, username: str) -> Optional["User"]:
        return cls.query.filter_by(username=username).first()


class Cart(db.Model):

    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=db.func.now())
    products = db.relationship(
        "Products", secondary=cart_products_association, backref="carts")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "quantity": self.quantity,
            "added_at": self.added_at
        }

    def __repr__(self) -> str:
        return f"<Cart user_id={self.user_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Products(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime, default=db.func.now())
    image_url = db.Column(db.String(256), nullable=False)
    score = db.Column(db.Float, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "added_at": self.added_at,
            "image_url": self.image_url,
            "score": self.score
        }

    def __repr__(self) -> str:
        return f"<Products name={self.name}> description={self.description}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
