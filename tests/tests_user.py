from auth_tests_base import TestBase
from parameterized import parameterized, parameterized_class
import datetime
from flask_login import current_user


class TestAuth(TestBase):

    def test_index(self):
        """Test if the index route return the correct message"""

        response = self.client.get("/apis/v1/user/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "Auth api v1", "status_code":  200})

    def test_client_connects_to_test_db(self):
        """Test if the client is connecting to the test database"""

        self.assertTrue(self.app.testing)

        # Get the database URI
        db_uri = self.app.config["SQLALCHEMY_DATABASE_URI"]
        db_name = db_uri.split("/")[-1]
        self.assertEqual(db_name, "alpha_store_mock")

    # register tests
    def test_register_route_wrong_method(self):
        """Test if the register route return the correct message when the method is wrong"""

        response = self.client.get("/apis/v1/user/register")

        self.assertEqual(response.status_code, 405)

    def test_register_route_no_data(self):
        """Test if the register route return the correct message when the method is wrong"""

        response = self.client.post("/apis/v1/user/register")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"message": "No input data provided", "status_code": 400})

    @parameterized.expand([
        ("password", {"username": "test", "email": "valid@mail.com"},
         "password: Missing data for required field."),
        ("email", {"username": "test", "password": "validPassword1@2"},
         "email: Missing data for required field."),
        ("username", {"email": "valid@mail.com", "password": "validPassword12@"},
         "username: Missing data for required field."),
    ])
    def test_register_route_missing_parameter(self, name, input, expected):

        expected_message = {
            'message': f"Invalid input data: {expected}", 'status_code': 400}
        response = self.client.post("/apis/v1/user/register", json=input)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_message)

    @parameterized.expand([
        ("invalid email", {"username": "test", "email": "invalid", "password": "validPassword!4"},
         "email: Not a valid email address."),  # (name, input, expected)
        ("invalid username", {"username": "n", "email": "valid@mail.com",
         "password": "validPassword!4"}, "username: Length must be between 4 and 20."),
        ("password too short", {"username": "test", "email": "valid@mail.com",
         "password": "invalid"}, "password: Shorter than minimum length 8."),
        ("pass no digts", {"username": "test", "email": "valid@mail.com",
         "password": "invalidPassword@"}, "password: Password must contain at least one digit"),
        ("pass no uppercase", {"username": "validname", "email": "valid@mail.com",
         "password": "123abc@1"}, "password: Password must contain at least one uppercase letter"),
        ("pass no lowercase", {"username": "validname", "email": "valid@mail.com",
         "password": "123ABC@1"}, "password: Password must contain at least one lowercase letter"),
        ("pass no symbol", {"username": "validname", "email": "valid@mail.com",
         "password": "ABC123abc", }, "password: Password must contain at least one special character"),
    ])
    def test_register_with_invalid_parameters(self, name, input, expected):

        expected_message = {
            'message': f"Invalid input data: {expected}", 'status_code': 400}
        response = self.client.post("/apis/v1/user/register", json=input)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_message)

    def test_register_with_valid_parameters(self):

        input_data = {"username": "validname",
                      "email": "valid@email.com", "password": "validPassword!4"}
        response = self.client.post("/apis/v1/user/register", json=input_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json, {"message": "User created successfully", "status_code": 201})

    @parameterized.expand([
        ("username", {"username": "test_user", "email": "validunique@mail.com",
         "password": "ValidPass@12"}, "username: Username already exists"),
        ("email", {"username": "validunique", "email": "testuser@validmail.com",
         "password": "ValidPass@12"}, "email: Email already exists"),
    ])
    def test_register_with_existing_field(self, name, input, expected):

        self.mock_user()

        expected_message = {
            'message': f"Invalid input data: {expected}", 'status_code': 400}
        response = self.client.post("/apis/v1/user/register", json=input)
        self.assertEqual(response.status_code, 400)

    def test_user_dict_method_and_repr(self):
        """
        Test if User.to_dict and __repr__ method works as expected.
        Since this tests are very simple, i'll test both at the same time
        """

        user = self.mock_user()
        user_dict = user.to_dict()
        joined_at = user_dict.get("joined_at", None)
        usr_repr_expected = f"<User username={user.username}, email={user.email}>"
        self.assertEqual(user_dict["username"], "test_user")
        self.assertEqual(user_dict["email"], "testuser@validmail.com")
        self.assertEqual(user_dict["id"], 1)
        self.assertEqual(True, isinstance(joined_at, datetime.datetime))
        self.assertEqual(usr_repr_expected, user.__repr__())

    # login tests

    def test_login_route_wrong_method(self):
        """Test if the login route return the correct message when the method is wrong"""

        response = self.client.get("/apis/v1/user/login")

        self.assertEqual(response.status_code, 405)

    @parameterized.expand([
        ("json", None, "No input data provided or missing required fields"),
        ("password", {"email": "test_user"},
         "No input data provided or missing required fields"),
        ("email", {"password": "ValidPass@12"},
         "No input data provided or missing required fields"),
    ])
    def test_login_route_missing_field(self, name, input, expected):
        """Test if the login route return the correct message when the method is wrong"""

        response = self.client.post("/apis/v1/user/login")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {
                         "message": "No input data provided or missing required fields", "status_code": 400})

    def test_login_with_inexistent_user(self):
        """Test if the login route return the correct message when the user doesn't exist"""

        input_data = {"email": "test_user", "password": "ValidPass@12"}
        response = self.client.post("/apis/v1/user/login", json=input_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json, {"message": "Invalid email or password", "status_code": 401})

    def test_login_with_wrong_password(self):
        """Test if the login route return the correct message when the password is wrong"""

        self.mock_user()
        input_data = {"email": "testuser@validmail.com",
                      "password": "wrongPassword"}
        response = self.client.post("/apis/v1/user/login", json=input_data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json, {"message": "Invalid email or password", "status_code": 401})

    def test_login_with_valid_credentials(self):
        """Test if the login route return the correct message when the password is wrong"""

        self.mock_user()
        input_data = {"email": "testuser@validmail.com",
                      "password": "Testpass12@"}
        response = self.client.post("/apis/v1/user/login", json=input_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Logged in successfully")
        self.assertEqual(True, current_user.is_authenticated)

    # logout tests
    def test_logout_route_wrong_method(self):
        """Test if the logout route return the correct message when the method is wrong"""

        response = self.client.get("/apis/v1/user/logout")

        self.assertEqual(response.status_code, 405)

    def test_logout_with_no_user_logged_in(self):
        """Test if the logout route return the correct message when the user is not logged in"""

        response = self.client.post("/apis/v1/user/logout")
        self.assertEqual(response.status_code, 401)

    def test_logout_with_user_logged_in(self):
        self.mock_login()
        response = self.client.post("/apis/v1/user/logout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "Logged out successfully", "status_code": 200})

    # Cart tests
    def test_add_to_cart_without_user_logged_in(self):
        """Test if the add to cart route return the correct message when the user is not logged in"""

        response = self.client.post("/apis/v1/user/cart/add-to-cart/1")
        self.assertEqual(response.status_code, 401)

    def test_add_to_cart_with_user_logged_in(self):
        self.mock_login()
        self.mock_product()
        response = self.client.post("/apis/v1/user/cart/add-to-cart/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "Product added to cart successfully", "status_code": 200})

    def test_add_to_cart_with_user_logged_in_and_invalid_product_id(self):

        self.mock_login()

        response = self.client.post("/apis/v1/user/cart/add-to-cart/1")
        self.assertEqual(response.status_code, 404)

    def test_add_to_cart_duplicate_product(self):
        self.mock_login()
        self.mock_product()

        # add product to cart twice
        # Since we have an earlier test that checks if the product is added to cart successfully
        # we can assume that the first request will be successful
        _ = self.client.post("/apis/v1/user/cart/add-to-cart/1")
        response = self.client.post("/apis/v1/user/cart/add-to-cart/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "Product added to cart successfully", "status_code": 200})

    def test_add_to_cart_same_product_different_user(self):
        self.mock_login()
        self.mock_product()

        # add to cart with user 1
        _ = self.client.post("/apis/v1/user/cart/add-to-cart/1")

        # logout
        _ = self.client.post("/apis/v1/user/logout")

        # login with user 2
        self.mock_login(username="test_user_2",
                        email="teste2@validmail.com", password="Testpass12@")

        response = self.client.post("/apis/v1/user/cart/add-to-cart/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "Product added to cart successfully", "status_code": 200})

    def test_get_cart_without_user_logged_in(self):
        """Test if the get cart route return the correct message when the user is not logged in"""

        response = self.client.get("/apis/v1/user/cart")
        self.assertEqual(response.status_code, 401)

    def test_get_cart_with_user_logged_in_and_empty_cart(self):

        self.mock_login()
        response = self.client.get("/apis/v1/user/cart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["products"], [])
        self.assertEqual(response.json["total_items"], 0)
        self.assertEqual(response.json["total_price"], 0)

    def test_get_cart_with_user_logged_in_and_products_in_cart(self):

        self.mock_login()
        self.mock_product()

        # add product to cart
        _ = self.client.post("/apis/v1/user/cart/add-to-cart/1")

        response = self.client.get("/apis/v1/user/cart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total_items"], 1)
        self.assertEqual(
            response.json["total_price"], self.mock_product_data["price"] + 10)
        self.assertEqual(response.json["products"][0]["id"], 1)

    def test_remove_from_cart_without_user_logged_in(self):
        """Test if the remove from cart route return the correct message when the user is not logged in"""

        response = self.client.post("/apis/v1/user/cart/remove-from-cart/1")
        self.assertEqual(response.status_code, 401)

    def test_remove_from_cart_with_user_logged_in_and_invalid_product_id(self):

        self.mock_login()
        response = self.client.post("/apis/v1/user/cart/remove-from-cart/a")
        self.assertEqual(response.status_code, 404)

    def test_remove_from_cart_with_user_logged_in_and_product_not_in_cart(self):

        self.mock_login()
        self.mock_product()

        response = self.client.post("/apis/v1/user/cart/remove-from-cart/1")
        self.assertEqual(response.status_code, 404)

    def test_remove_from_cart_with_user_logged_in_and_product_in_cart(self):

        self.mock_login()
        self.mock_product()

        # add product to cart
        _ = self.client.post("/apis/v1/user/cart/add-to-cart/1")

        response = self.client.post("/apis/v1/user/cart/remove-from-cart/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "Product removed from cart successfully", "status_code": 200})

    # Checkout tests
    def test_checkout_without_logged_user(self):

        response = self.client.post("/apis/v1/user/cart/checkout")

        self.assertEqual(response.status_code, 401)

    def test_checkout_with_logged_user_and_empty_cart(self):

        self.mock_login()
        response = self.client.post("/apis/v1/user/cart/checkout")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"message": "Cart is empty", "status_code": 400})

    def test_checkout_with_logged_user_and_products_in_cart(self):

        self.mock_login()
        self.mock_product()

        # add product to cart
        _ = self.client.post("/apis/v1/user/cart/add-to-cart/1")

        response = self.client.post("/apis/v1/user/cart/checkout")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "Checkout successfully", "status_code": 200})

        # Verify if the user cart is empty
        response = self.client.get("/apis/v1/user/cart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["products"], [])
