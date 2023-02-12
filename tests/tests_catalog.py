from auth_tests_base import TestBase
from parameterized import parameterized


class TestCatalog(TestBase):

    def test_index(self):
        """Test if the index route return the correct message"""

        response = self.client.get("/apis/v1/catalog/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "Catalog api v1", "status_code":  200})

    def test_get_item_by_id_inexistent(self):
        """Test if the get_item_by_id route return the correct message when the item doesn't exist"""

        response = self.client.get("/apis/v1/catalog/get_products_by_id/100")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json, {"message": "Product not found", "status_code": 404, "product": {}})

    def test_get_item_by_id_existent(self):
        """Test if the get_item_by_id route return the correct message when the item exists"""

        self.mock_product()
        response = self.client.get("/apis/v1/catalog/get_products_by_id/1")

        response_product = response.json["product"]
        response_product.pop("added_at", None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Product found")
        self.assertEqual(response.json["status_code"], 200)
        self.assertEqual(
            response_product["name"], self.mock_product_data["name"])

    def test_get_item_by_name_inexistent(self):
        """Test if the get_item_by_name route return the correct message when the item doesn't exist"""

        response = self.client.get("/apis/v1/catalog/get_products_by_name/100")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json, {"message": "Product not found", "status_code": 404, "product": {}})

    def test_get_item_by_name_existent(self):
        """Test if the get_item_by_name route return the correct message when the item exists"""

        self.mock_product()
        response = self.client.get(
            f"/apis/v1/catalog/get_products_by_name/{self.mock_product_data['name']}")

        response_product = response.json["product"]
        response_product.pop("added_at", None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Product found")
        self.assertEqual(response.json["status_code"], 200)
        self.assertEqual(
            response_product["name"], self.mock_product_data["name"])

    def test_get_products(self):
        """Test if the get_products route return the correct message"""

        self.mock_product()

        response = self.client.get("/apis/v1/catalog/get_products")

        response_product = response.json["products"][0]
        response_product.pop("added_at", None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Products found")
        self.assertEqual(response.json["status_code"], 200)
        self.assertEqual(
            response_product["name"], self.mock_product_data["name"])

    def test_get_products_empty(self):
        """
        Test the get_products route when there are no products in the database
        """

        response = self.client.get("/apis/v1/catalog/get_products")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {"message": "No products found", "status_code": 200, "products": []})

    # Parameter Format:
    # (test_name, (sort_by, sort_type, product_data), expected_return_position)
    @parameterized.expand([
        ("name", ("name", "asc", {'name': 'A',
         'price': 9999, 'score': 9999}), 0),
        ("name", ("name", "desc", {'name': 'A',
                                   'price': 1, 'score': 1}), 1),
        ("price", ("price", "asc", {'name': 'Z', 'price': 1, 'score': 1}), 0),
        ("price", ("price", "desc", {
         'name': 'A', 'price': 9999, 'score': 1}), 0),
        ("score", ("score", "asc", {
         "name": "Z", "price": 9999, "score": 1}), 0),
        ("score", ("score", "desc", {
         "name": "A", "price": 1, "score": 9999}), 0),
    ])
    def test_get_products_sorted_by_column(self, _, test_input, expected):

        sort_by, sort_type, product_data = test_input

        # This product will be the standard for the test
        self.mock_product()

        self.mock_product(
            name=product_data["name"], price=product_data["price"], score=product_data["score"])

        response = self.client.get(
            f"/apis/v1/catalog/get_products?sort_by={sort_by}&sort_type={sort_type}"
        )

        # Expected position of the standard product in the response list
        expected_position = response.json["products"][expected]
        expected_position.pop("added_at", None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Products found")
        self.assertEqual(expected_position["name"], product_data["name"])
        self.assertEqual(expected_position["price"], product_data["price"])
        self.assertEqual(expected_position["score"], product_data["score"])

    def test_get_product_with_invalid_sort_by(self):
        """
        Test the get_products route when the sort_by parameter is invalid
        """

        # If dont have any product, the api will return 200, but with an empty list
        # So, i will need to mock a product to test the invalid sort_by parameter
        self.mock_product()

        response = self.client.get(
            "/apis/v1/catalog/get_products?sort_by=invalid&sort_type=asc")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"message": "Invalid sort_by field: invalid", "status_code": 400})

    def test_get_product_with_invalid_sort_type(self):
        """
        Test the get_products route when the sort_type parameter is invalid
        """

        # If dont have any product, the api will return 200, without check order parameters
        # So, i will need to mock a product to test the invalid sort_by parameter
        self.mock_product()

        response = self.client.get(
            "/apis/v1/catalog/get_products?sort_by=name&sort_type=invalid")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"message": "Invalid sort_type field: invalid", "status_code": 400})
