from flask import Blueprint, request, jsonify, make_response, Flask, current_app
from flask_login import login_user, logout_user, login_required, current_user
from alpha_store.auth.serializer import UserSchema
from alpha_store.models import User
from marshmallow import ValidationError

auth = Blueprint("auth", __name__, url_prefix="/apis/v1/user")


def configure(app: Flask) -> None:

    app.register_blueprint(auth)
    app.logger.info("Auth configured")


@auth.route("/", methods=["GET"])
def index():

    return {
        "message": "Auth api v1",
        "status_code": 200,
    }, 200


@auth.route("/register", methods=["POST"])
def register():
    """
    This endpoint handles the user registration.
    It's purpose is to process a JSON payload containing the user registration information, validate it, and if successful, persist the user data in the db.
    The function starts by extracting the JSON data from the request using the request.get_json method. 
    If no JSON data is provided, the function returns a response with a "No input data provided" error message and a 400 Bad Request status code.
    Next, the function attempts to load the user data into a UserSchema instance using the user_schema.load method.
    This will validate the input data, and if successful, create a user instance.
    If an error occurs during validation, a ValidationError is raised and the first error message is extracted and returned in the response along with a 400 Bad Request status code.
    Finally, if the user is successfully created, a success message is returned along with a 201 Created status code.

    The expected JSON payload is as follows:
    {
        'email': 'valid@supersecretmail.com',
        'username': 'validusername',
        'password': 'validpassword'
    }

    The password is hashed using the werkzeug.security.generate_password_hash method and
    must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number and one special character.


    :return: A JSON response containing the status code and a message

    """

    json_data = request.get_json(silent=True)

    if not json_data:
        return {
            "message": "No input data provided",
            "status_code": 400,
        }, 400

    try:

        user_schema = UserSchema()
        user = user_schema.load(json_data)

        current_app.logger.debug(f"User {user.username} created successfully")

        # Return the data
        return {
            "message": "User created successfully",
            "status_code": 201,
        }, 201

    except ValidationError as exc:
        # In this application, the serializer have the responsibility to validate the data, including the uniqueness of the username and email
        # So, if the data is invalid, it will raise a ValidationError
        # With that, the responsiblity of the view is just manage the response
        first_raised_error = list(exc.messages.items())[0]
        return {
            "message": f"Invalid input data: {first_raised_error[0]}: {first_raised_error[1][0]}",
            "status_code": 400,
        }, 400


@auth.route("/login", methods=["POST"])
def login():
    """
    This endpoint handles the user login. 
    It loads the JSON data from the request, validates it, and if successful, logs the user in.
    The email and password are extracted before, and if one of them are not provided,
    a response with a "No input data provided or missing required fields" error message and a 400 Bad Request status code is returned.

    The ``login_user`` function from Flask-Login is used to log the user in. It saves the user login status in the session.
    When the user is logged in, the ``current_user`` variable is set to the user instance.
    Everytime that the user tries to access a protected route, the ``login_required`` decorator will check if the user is logged in.

    The expected JSON payload is as follows:
    {
        "email": "supervalid@mail.com",
        "password": "supervalidpassword"
    }

    """
    try:
        json_data = request.get_json(silent=True)

        email = json_data["email"]
        password = json_data["password"]

        usr = User.get_user_by_email(email)

        if usr and usr.check_password(password):
            login_user(usr)
            return {
                "message": "Logged in successfully",
                "status_code": 200,
            }, 200

        return {
            "message": "Invalid email or password",
            "status_code": 401,
        }, 401

    except (KeyError, TypeError) as exc:
        current_app.logger.debug(
            f"Input data error with loggin attempt: {exc}")
        return {
            "message": "No input data provided or missing required fields",
            "status_code": 400,
        }, 400


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    This endpoint handles the user logout.
    The logout_user function from Flask-Login is used to log the user out. It clears the user login status in the session.
    """

    logout_user()
    return {
        "message": "Logged out successfully",
        "status_code": 200,
    }, 200


@auth.route("/cart", methods=["GET"])
@login_required
def get_cart():
    """
    This endpoint handles the user cart retrieval. 
    It will call ``current_user.get_cart`` method to retrieve the user cart.
    Also, the shipping_cost and total_price is calculated and returned in the response.
    Note: The shipping cost is 10 for each product, but if the total shipping cost is greater than or equals to 250, it will be free. 

    :return: A JSON response containing the status code, the cart id, the products, the total price, the shipping cost and the total items
    """

    user_cart = current_user.get_cart()

    # calculate the total price of the cart
    total_price = 0
    shipping_cost = 0
    for product in user_cart.get("products", []):
        total_price += product["price"]
        shipping_cost += 10

    shipping_cost = shipping_cost if shipping_cost <= 250 else 0
    total_price += shipping_cost

    return {
        "message": "Cart retrieved successfully",
        "status_code": 200,
        "cart_id": user_cart["cart_id"],
        "products": user_cart["products"],
        "total_price": total_price,
        "shipping_cost": shipping_cost,
        "total_items": len(user_cart["products"]),
    }, 200


@auth.route("/cart/add-to-cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    try:
        current_user.add_to_cart(product_id)
        return {
            "message": "Product added to cart successfully",
            "status_code": 200,
        }, 200

    # The add_to_cart method will raise an exception if the product is not found
    except ValueError as _:
        current_app.logger.debug(
            f"Product {product_id} not found when attempting to add to cart")
        return {
            "message": "Product not found",
            "status_code": 404,
        }, 404


@auth.route("/cart/remove-from-cart/<int:product_id>", methods=["POST"])
@login_required
def remove_from_cart(product_id):
    """
    This endpoint handles the product removal from the user cart.
    It will call ``current_user.remove_from_cart`` method to remove the product from the user cart.
    If the product is not found or not in the cart, a 404 Not Found status code is returned.

    """
    try:
        current_user.remove_from_cart(product_id)
        return {
            "message": "Product removed from cart successfully",
            "status_code": 200,
        }, 200

    except ValueError as exc:
        current_app.logger.debug(
            f"Product {product_id} not found or not in cart when attempting to remove from cart: {exc}")
        return {
            "message": "Product not found or not in cart",
            "status_code": 404,
        }, 404


@auth.route("/cart/checkout", methods=["POST"])
@login_required
def checkout():
    """
    This endpoint handles the user cart checkout.
    It will call ``current_user.checkout`` method to checkout the user cart.
    If the cart is empty, a 400 Bad Request status code is returned.
    All the products in the cart will be removed from the cart and added to the user orders. Also,
    the shipping_cost and total_price is calculated and returned in the response.
    At this time, the total_price and shipping_cost are saved in the order table(Different from the cart table,
    where the shipping_cost and total_price are calculated dynamically).
    When the checkout is successful, it will be registered in SalesOrder table too, but without any info
    """
    try:
        current_user.checkout()
        return {
            "message": "Checkout successfully",
            "status_code": 200,
        }, 200

    except ValueError as _:
        return {
            "message": "Cart is empty",
            "status_code": 400,
        }, 400


@auth.route("/orders", methods=["GET"])
@login_required
def get_orders():
    """
        Fetches the user orders.
        It will call ``current_user.get_orders`` method to retrieve the user orders.
        :return: A JSON response containing the status code, the orders
    """

    orders = current_user.get_orders()

    return {
        "message": "Orders retrieved successfully",
        "status_code": 200,
        "orders": orders,
    }, 200


@auth.errorhandler(401)
def unauthorized(error):
    return {
        "message": "Unauthorized",
        "status_code": 401,
    }, 401
