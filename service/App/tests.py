import random
import string
import unittest
import base64

import requests as rq



def get_random_user():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class TestPassTheHashVuln(unittest.TestCase):
    def test_pth(self):
        obj = {
            'username': 'HNYDUW0MHB',
            'password': base64.b64encode(bytes.fromhex('3B89BCF90E89EDCDED3A5A2C9EF09B42E4DC8C6546684673D94075C54F31B6B4')).decode('ascii'),
            'login': 'signin'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(302, req.status_code)

    def test_pth(self):
        obj = {
            'username': 'HNYDUW0MHB',
            'password': base64.b64encode(bytes.fromhex('3B89BCF90E89EDCDED3A5A2C9EF09B42E4DC8C6546684673D94575C54F31B6B4')).decode('ascii'),
            'login': 'signin'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(401, req.status_code)


class TestSimpleLogin(unittest.TestCase):
    def test_create_user(self):
        user = get_random_user()
        obj = {
            'username': user,
            'password': base64.b64encode(b'mysecretpass').decode('ascii'),
            'login': 'signup'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(302, req.status_code)

    def test_check_user(self):
        user = get_random_user()
        obj = {
            'username': user,
            'password': base64.b64encode(b'mysecretpass').decode('ascii'),
            'login': 'signup'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(302, req.status_code)
        obj['login'] = 'signin'
        req2 = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(302, req2.status_code)
        obj['password'] = base64.b64encode(b'mysecretPass').decode('ascii')
        req3 = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(401, req3.status_code)

    def test_duplicate_user(self):
        user = get_random_user()
        obj = {
            'username': user,
            'password': base64.b64encode(b'mysecretpass').decode('ascii'),
            'login': 'signup'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(302, req.status_code)
        req2 = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(401, req2.status_code)


if __name__ == '__main__':
    unittest.main()

