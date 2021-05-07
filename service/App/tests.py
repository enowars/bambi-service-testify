import random
import string
import unittest
from src import userDBConnecter as db


def get_random_user():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class TestDBCOnnector(unittest.TestCase):
    def test_user_create(self):
        user = get_random_user()
        db.create_user(user, "secretpass")
        self.assertTrue(db.check_user(user, "secretpass"))
        self.assertFalse(db.check_user(user, "secretpass1"))

    def test_invalid_user(self):
        self.assertFalse(db.check_user("user", "secretpass1"))

    def test_user_already_used(self):
        user = get_random_user()
        self.assertTrue(db.create_user(user, "secretpass"))
        self.assertFalse(db.create_user(user, "secretpass"))

    def setUp(self) -> None:
        db.set_hostname("localhost")


if __name__ == '__main__':
    unittest.main()

