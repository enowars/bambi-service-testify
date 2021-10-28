#!/usr/bin/env python3

import base64, faker, logging, random, re, secrets, string, time

from enochecker import BaseChecker, BrokenServiceException, EnoException, run
from enochecker.utils import assert_in

from bs4 import BeautifulSoup

logging.getLogger('faker').setLevel(logging.ERROR)


def get_random_string(n):
    alphabet = string.ascii_letters + string.digits
    return "".join([secrets.choice(alphabet) for i in range(n)])


def get_profile():
    fake = faker.Faker()
    fake.seed_instance(secrets.randbits(256))
    profile = fake.simple_profile()
    return {
        'username': profile['username'] + get_random_string(30),
        'password': get_random_string(30),
        'prename': profile['name'].split()[0],
        'lastname': profile['name'].split()[-1],
        'date': profile['birthdate'].strftime('%Y-%m-%d'),
        'time': fake.time(pattern='%H:%M'),
        'file': fake.text(),
        'filename': "badge.png",
        'pin': get_random_string(30)
    }


class testifyChecker(BaseChecker):
    ##### EDIT YOUR CHECKER PARAMETERS
    flag_variants = 2
    noise_variants = 1
    havoc_variants = 7
    exploit_variants = 2
    service_name = "testify"
    port = 8597  # The port will automatically be picked up as default by self.connect and self.http.

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
        assert_in('consider uploading your ID', res.text, 'login failed: not redirected to appointment page')

    def make_appointment(self, prename, lastname, filename, date, time, file, doctor, pin, extra='info'):
        """
        makes appointment using flag as prename, filename
        returns appointment id
        """
        data = {
            'prename': prename,
            'lastname': lastname,
            'date': date,
            'time': time,
            'doctor': doctor,
            'extra': extra,
            'pin': pin
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

    def get_appointment(self, session_id):
        kwargs = {
            'allow_redirects': True
        }
        resp = self.http_get('/appointments', **kwargs)
        return resp

    def putflag(self):  # type: () -> None
        if self.variant_id == 0:
            profile = get_profile()
            self.register(profile['username'], profile['password'])
            appointment_id = self.make_appointment(self.flag,
                profile['lastname'], profile['filename'], profile['date'], profile['time'],
                profile['file'], 'doctor0' + str(random.randint(1, 5)), profile['pin'])

            # store in db
            self.chain_db = {
                "profile": profile,
                "app_id": appointment_id
            }
            self.debug('successfully made appointment %s' % appointment_id)

        elif self.variant_id == 1:
            profile = get_profile()
            self.register(profile['username'], profile['password'])
            appointment_id = self.make_appointment(profile['prename'], profile['lastname'],
                profile['filename'], profile['date'], profile['time'], profile['file'],
                'doctor0' + str(random.randint(1, 5)), profile['pin'], self.flag)

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
            except Exception as ex:
                self.debug(f"error getting profile from db: {ex}")
                raise BrokenServiceException("Previous putflag failed.")

            # Let's login to the service
            session_id = self.login(profile['username'], profile['password'])
            resp = self.get_appointment(session_id)

            assert_in(self.flag, resp.text, "Resulting flag was found to be incorrect")
        elif self.variant_id == 1:
            # First we check if the previous putflag succeeded!
            try:
                profile = self.chain_db["profile"]
                app_id = self.chain_db["app_id"]
            except Exception as ex:
                self.debug(f"error getting profile from db: {ex}")
                raise BrokenServiceException("Previous putflag failed.")
            kwargs = {
                'data': {'app_id': app_id, 'pin': profile['pin']},
                'allow_redirects': True
            }
            res = self.http_post('/appointment_info', **kwargs)
            if res.text.find('Your message') == -1:
                raise BrokenServiceException("could not retrieve appointment info")
            assert_in(self.flag, res.text, "Resulting flag was found to be incorrect")
        else:
            raise EnoException("Wrong variant_id provided")

    def putnoise(self):  # type: () -> None
        if self.variant_id == 0:
            profile = get_profile()
            username = profile['username']
            password = profile['password']
            self.register(username, password)
            app_id = self.make_appointment(profile['prename'], profile['lastname'], profile['filename'],
                                           profile['date'], profile['time'], profile['file'], 'doctor0' + str(random.randint(1, 5)), profile['pin'])

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
            assert_in(profile['file'], resp.text, "Resulting file found to be incorrect")
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
            # test create user and login
            profile = get_profile()
            username = profile['username']
            password = profile['password']
            self.register(username, password)
            self.login(username, password)
        elif self.variant_id == 2:
            # test show online users
            profile1 = get_profile()
            self.register(profile1['username'], profile1['password'])
            resp = self.http_get('/about')
            self.debug(resp.text)
            assert_in(" " + profile1['username'] + " ", resp.text,
                    f'username {profile1["username"]} not found in online users')
        elif self.variant_id == 3:
            # test restore username
            profile = get_profile()
            self.register(profile['username'], profile['password'])
            kwargs = {
                'data': {'email': profile['username'] + '@' + profile['username'] + '.de'}
            }
            resp = self.http_post('/restore_username', **kwargs)
            self.debug(resp.text)
            assert_in('Your username is:', resp.text, 'username could not be restored')
            assert_in(profile['username'], resp.text, 'wrong username provided in response')

        elif self.variant_id == 4:
            # test duplicate user registration
            profile = get_profile()
            self.register(profile['username'], profile['password'])
            try:
                self.register(profile['username'], profile['password'])
                raise BrokenServiceException("duplicate registration passed")
            except EnoException as e:
                pass
        elif self.variant_id == 5:
            # test appointment info endpoint
            profile = get_profile()
            info = get_random_string(30)
            self.register(profile['username'], profile['password'])
            app_id = self.make_appointment(profile['prename'], profile['lastname'], profile['filename'],
                    profile['date'], profile['time'], profile['file'], 'doctor0' + str(random.randint(1, 5)),
                    profile['pin'], info)
            kwargs = {
                'allow_redirects': True,
                'data': {'app_id': app_id,
                         'pin': profile['pin']}
            }
            res = self.http_post('/appointment_info', **kwargs)
            assert_in(info, res.text, f"could not receive placed info {info} from appointment_info")
        elif self.variant_id == 6:
            # test doctors page
            profile = get_profile()
            self.register(profile['username'], profile['password'])
            kwargs = {
                'data': { 'patient_username': profile['username'] },
                'allow_redirects': True
            }
            text = self.http_post('/doctors', **kwargs).text
            assert_in('not authenticated!', text, '/doctors endpoint not working!')
        else:
            raise EnoException("Wrong variant_id provided")

    def exploit(self):
        if self.variant_id > 1:
            raise EnoException("Wrong variant_id provided")
        elif self.variant_id == 0:

            raise BrokenServiceException("Resulting flag was found to be incorrect")

        elif self.variant_id == 1:
            profile = get_profile()
            username = profile['username']
            password = profile['password']

            self.register(username, password)

            app_id = self.make_appointment(profile['prename'], profile['lastname'], profile['filename'], profile['date'],
                    profile['time'], profile['file'], username, profile['pin'])

            text = self.http_get('/about').text
            soup = BeautifulSoup(text, "html.parser")
            users = soup.select_one("#onlineUsers > div").text.strip().split("  -  ")
            for u in users:
                kwargs = {
                    'data': { 'patient_username': u },
                    'allow_redirects': True
                }
                resp = self.http_post('/doctors', **kwargs).text
                if flag := self.search_flag(resp):
                    return flag

            raise BrokenServiceException('Could not find flag in doctor note')


app = testifyChecker.service  # This can be used for uswgi.
if __name__ == "__main__":
    run(testifyChecker)
