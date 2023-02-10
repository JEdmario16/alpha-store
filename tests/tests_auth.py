from auth_tests_base import AuthTestBase
from parameterized import parameterized, parameterized_class

class TestAuth(AuthTestBase):

    def test_index(self):

        """Test if the index route return the correct message"""

        response = self.client.get("/apis/v1/auth/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Auth api v1", "status_code":  200})

    def test_client_connects_to_test_db(self):

        """Test if the client is connecting to the test database"""

        self.assertTrue(self.app.testing)
        
        # Get the database URI
        db_uri = self.app.config["SQLALCHEMY_DATABASE_URI"]
        db_name = db_uri.split("/")[-1]
        self.assertEqual(db_name, "alpha_store_mock")

    ## register tests
    def test_register_route_wrong_method(self):

        """Test if the register route return the correct message when the method is wrong"""

        response = self.client.get("/apis/v1/auth/register")

        self.assertEqual(response.status_code, 405)

    def test_register_route_no_data(self):
            """Test if the register route return the correct message when the method is wrong"""
    
            response = self.client.post("/apis/v1/auth/register")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json, {"message": "No input data provided", "status_code": 400})


    @parameterized.expand([
        ({"username": "test", "email": "valid@mail.com"}, "password"),
        ({"username": "test", "password": "asdas"}, "email"),
        ({"email": "valid@mail.com", "password": "asdas"}, "username"),
        ({"password": "asdas"}, "username"),
        ({"email": "valid@mail.com"}, "username"),
        ({"username": "test"}, "email"),
    ])
    def test_register_route_missing_key(self, input, expected):

        response = self.client.post("/apis/v1/auth/register", json=input)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": f"Missing key: '{expected}'", "status_code": 400})


    


