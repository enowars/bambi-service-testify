import random
import string
import unittest
from src import userDBConnecter as db


class TestDBCOnnector(unittest.TestCase):
    def test_user_create(self):
        user = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        db.create_user(user, "secretpass")
        self.assertTrue(db.check_user(user, "secretpass"))
        self.assertFalse(db.check_user(user, "secretpass1"))


if __name__ == '__main__':
    unittest.main()

