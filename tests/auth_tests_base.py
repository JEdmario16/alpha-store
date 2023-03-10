from unittest import TestCase
from alpha_store.main import create_app
from alpha_store.models import User, Products
from typing import Optional


class TestBase(TestCase):


    def setUp(self):

        self.app = create_app(test_mode=True)
        self.app.testing = True
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.app.db.create_all()

        self.mock_user_data = {
            "username": "test_user",
            "email": "testuser@validmail.com",
            "password": "Testpass12@"
        }

        self.mock_product_data = {
            "name": "Test Product",
            "description": "Test Product Description",
            "price": 10.00,
            "score": 100,
            "image_url": "https://test.com/image.png",
            "id": 1,
            "category": "Test Category",
            "release_date": "2017-10-27T03:00:00.000Z",
        }

    def tearDown(self) -> None:
        self.app.db.session.remove()
        self.app.db.drop_all()
        self.app_context.pop()

    def mock_user(self, username: Optional[str] = None, email: Optional[str] = None, password: Optional[str] = None) -> User:
        """Mock a user for testing purposes. If no data is provided, it will use the ``self.mock_user_data``"""

        username = username or self.mock_user_data["username"]
        email = email or self.mock_user_data["email"]
        password = password or self.mock_user_data["password"]

        user = User(username=username, email=email, password=password)
        user.save()

        return user

    def mock_login(self, username: Optional[str] = None, email: Optional[str] = None, password: Optional[str] = None):
        """
        Mock a login for testing purposes. If no data is provided, it will use the ``self.mock_user_data``
        This method calls the ``mock_user`` method to create a user and then login with it
        """
        username = username or self.mock_user_data["username"]
        email = email or self.mock_user_data["email"]
        password = password or self.mock_user_data["password"]

        user = self.mock_user(
            username=username, email=email, password=password)

        input_data = {"email": user.email, "password": password}
        _ = self.client.post("/apis/v1/user/login", json=input_data)
    

    def mock_product(self, name: Optional[str] = None, description: Optional[str] = None, price: Optional[float] = None, score: Optional[int] = None, image_url: Optional[str] = None, category: Optional[str] = None, release_date: Optional[str] = None) -> Products:
        """Mock a product for testing purposes. If no data is provided, it will use the ``self.mock_product_data``"""

        name = name or self.mock_product_data["name"]
        description = description or self.mock_product_data["description"]
        price = price or self.mock_product_data["price"]
        score = score or self.mock_product_data["score"]
        image_url = image_url or self.mock_product_data["image_url"]
        category = category or self.mock_product_data["category"]
        release_date = release_date or self.mock_product_data["release_date"]

        product = Products(name=name, description=description,
                           price=price, score=score, image_url=image_url, category=category, release_date=release_date)
        product.save()
        return product
