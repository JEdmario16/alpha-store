from unittest import TestCase
from alpha_store.main import create_app


class AuthTestBase(TestCase):

    def setUp(self):

        self.app = create_app(test_mode=True)
        self.app.testing = True
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.app.db.create_all()

    def tearDown(self) -> None:
            self.app.db.drop_all()
            self.app.db.session.remove()
            self.app_context.pop()
