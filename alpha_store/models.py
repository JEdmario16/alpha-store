import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from typing import Union, Optional


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
    db.Column('product_id', db.Integer,
              db.ForeignKey('products.id'))
)

order_products_association = db.Table(
    'order_product', db.Model.metadata,
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'))
)


class User(db.Model, UserMixin):

    """
    Store the user information
    All operations that need to be done with the user(like user cart, orders, etc) will be done here 
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True,
                         unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    joined_at = db.Column(db.DateTime, default=db.func.now())

    # One to one relationship with cart
    cart = db.relationship("Cart", backref="user", uselist=False)

    # One to many relationship with orders
    orders = db.relationship("Order", backref="user", uselist=True)

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

    def add_to_cart(self, product_id: int):
        """
        Search for given product id and add it to the user cart if it exists
        This method is called by the ``apis/v1/users/cart/add-to-cart`` endpoint
        """
        product = Products.query.filter_by(id=product_id).first()
        if not product:
            raise ValueError("Product not found")

        if not self.cart:
            self.cart = Cart()
            self.cart.save()

        self.cart.products.append(product)
        db.session.commit()

    def get_cart(self) -> dict:
        if not self.cart:
            self.cart = Cart()
            self.cart.save()

        return {
            "cart_id": self.cart.id,
            "added_at": self.cart.added_at,
            "products": [product.to_dict() for product in self.cart.products]
        }

    def remove_from_cart(self, product_id: int):

        product = Products.query.filter_by(id=product_id).first()
        if not product:
            raise ValueError("Product not found")

        if not self.cart:
            self.cart = Cart()
            self.cart.save()

        # check if product is in cart
        if product not in self.cart.products:
            raise ValueError("Product not in cart")

        self.cart.products.remove(product)
        db.session.commit()

    def checkout(self):

        if not self.cart:
            raise ValueError("Cart is empty")

        order = Order(user_id=self.id, total_price=0, shipping_cost=0)
        order.save()

        total_price = 0
        shipping_cost = 0

        for product in self.cart.products:
            total_price += product.price
            shipping_cost += 10
            order.products.append(product)

        order.total_price = total_price
        order.shipping_cost = shipping_cost if shipping_cost <= 250 else 0

        db.session.delete(self.cart)
        db.session.commit()

        # Everything went well, then register the order in ``SalesRecord`` table
        # This table don't stores any user information, just the product id and price
        recorded_sales = []
        for product in order.products:
            recorded_sales.append(SalesRecord(
                product_id=product.id,
                product_price=product.price,
                product_category=product.category
            ))

        db.session.bulk_save_objects(recorded_sales)
        db.session.commit()

    def get_orders(self) -> list:
        return [order.to_dict() for order in self.orders]

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
    category = db.Column(db.String(64), nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    added_at = db.Column(db.DateTime, default=db.func.now())
    image_url = db.Column(db.String(256), nullable=False)
    score = db.Column(db.Float, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "release_date": self.release_date,
            "added_at": self.added_at,
            "image_url": self.image_url,
            "score": self.score
        }

    def __repr__(self) -> str:
        return f"<Products name={self.name}> description={self.description}>"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=db.func.now())
    total_price = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)

    products = db.relationship(
        "Products", secondary=order_products_association, backref="orders")

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "added_at": self.added_at,
            "total_price": self.total_price,
            "shipping_cost": self.shipping_cost,
            "products": [product.to_dict() for product in self.products]
        }

    def __repr__(self) -> str:
        return f"<Order user_id={self.user_id}>"


class SalesRecord(db.Model):

    """
    This table will record all completes sale in this application and will be used in analytics package
    It just stores the product id and price, no user information is stored
    Also, the ``product_id`` is not a foreign key, because the product can be deleted from the database
    """

    __tablename__ = "sales_record"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    product_category = db.Column(db.String(64), nullable=True)
    sale_date = db.Column(db.DateTime, default=db.func.now())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_price": self.product_price,
            "product_category": self.product_category,
            "sale_date": self.sale_date
        }

    def __repr__(self) -> str:
        return f"<SalesRecord product_id={self.product_id}>"
