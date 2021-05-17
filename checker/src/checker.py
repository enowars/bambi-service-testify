#!/usr/bin/env python3
import base64
import re

from enochecker import BaseChecker, BrokenServiceException, EnoException, run
from enochecker.utils import SimpleSocket, assert_equals, assert_in
import random
import string


#### Checker Tenets
# A checker SHOULD not be easily identified by the examination of network traffic => This one is not satisfied, because our usernames and notes are simple too random and easily identifiable.
# A checker SHOULD use unusual, incorrect or pseudomalicious input to detect network filters => This tenet is not satisfied, because we do not send common attack strings (i.e. for SQL injection, RCE, etc.) in our notes or usernames.
####


def get_random_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class testifyChecker(BaseChecker):
    """
    Change the methods given here, then simply create the class and .run() it.
    Magic.
    A few convenient methods and helpers are provided in the BaseChecker.
    ensure_bytes ans ensure_unicode to make sure strings are always equal.
    As well as methods:
    self.connect() connects to the remote server.
    self.get and self.post request from http.
    self.chain_db is a dict that stores its contents to a mongodb or filesystem.
    conn.readline_expect(): fails if it's not read correctly
    To read the whole docu and find more goodies, run python -m pydoc enochecker
    (Or read the source, Luke)
    """

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

    def make_appointment(self, flag, filename, username, password):
        self.register(username, password)
        data = {
            'prename': flag,
            'lastname': 'Meyer',
            'date': '2021-05-06',
            'time': '02:56'
        }
        files = {'id_image': (filename, "test id document", 'application/octet-stream')}

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
        """
        This method stores a flag in the service.
        In case multiple flags are provided, self.variant_id gives the appropriate index.
        The flag itself can be retrieved from self.flag.
        On error, raise an Eno Exception.
        :raises EnoException on error
        :return this function can return a result if it wants
                if nothing is returned, the service status is considered okay.
                the preferred way to report errors in the service is by raising an appropriate enoexception
        """
        if self.variant_id == 0:
            username = get_random_string()
            password = get_random_string()
            appointment_id = self.make_appointment(self.flag, "filename", username, password)

            # store in db
            self.chain_db = {
                "username": username,
                "password": password,
                "app_id": appointment_id,
            }
            self.debug('successfully made appointment %s' % appointment_id)

        else:
            raise EnoException("Wrong variant_id provided")

    def getflag(self):  # type: () -> None
        """
        This method retrieves a flag from the service.
        Use self.flag to get the flag that needs to be recovered and self.round to get the round the flag was placed in.
        On error, raise an EnoException.
        :raises EnoException on error
        :return this function can return a result if it wants
                if nothing is returned, the service status is considered okay.
                the preferred way to report errors in the service is by raising an appropriate enoexception
        """
        if self.variant_id == 0:
            # First we check if the previous putflag succeeded!
            try:
                username: str = self.chain_db["username"]
                password: str = self.chain_db["password"]
                app_id: str = self.chain_db["app_id"]
            except IndexError as ex:
                self.debug(f"error getting notes from db: {ex}")
                raise BrokenServiceException("Previous putflag failed.")

            # Let's login to the service
            session_id = self.login(username, password)
            resp = self.get_appointment(session_id)

            assert_in(self.flag, resp.text, "Resulting flag was found to be incorrect")
        else:
            raise EnoException("Wrong variant_id provided")

    def putnoise(self):  # type: () -> None
        """
        This method stores noise in the service. The noise should later be recoverable.
        The difference between noise and flag is, that noise does not have to remain secret for other teams.
        This method can be called many times per round. Check how often using self.variant_id.
        On error, raise an EnoException.
        :raises EnoException on error
        :return this function can return a result if it wants
                if nothing is returned, the service status is considered okay.
                the preferred way to report errors in the service is by raising an appropriate enoexception
        """
        if self.variant_id == 0:
            self.debug(f"Connecting to the service")
            conn = self.connect()
            welcome = conn.read_until(">")

            # First we need to register a user. So let's create some random strings. (Your real checker should use some better usernames or so [i.e., use the "faker¨ lib])
            username = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=12)
            )
            password = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=12)
            )
            randomNote = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=36)
            )

            # Register another user
            self.register_user(conn, username, password)

            # Now we need to login
            self.login_user(conn, username, password)

            # Finally, we can post our note!
            self.debug(f"Sending command to save a note")
            conn.write(f"set {randomNote}\n")
            conn.read_until(b"Note saved! ID is ")

            try:
                noteId = conn.read_until(b"!\n>").rstrip(b"!\n>").decode()
            except Exception as ex:
                self.debug(f"Failed to retrieve note: {ex}")
                raise BrokenServiceException("Could not retrieve NoteId")

            assert_equals(len(noteId) > 0, True, message="Empty noteId received")

            self.debug(f"{noteId}")

            # Exit!
            self.debug(f"Sending exit command")
            conn.write(f"exit\n")
            conn.close()

            self.chain_db = {
                "username": username,
                "password": password,
                "noteId": noteId,
                "note": randomNote,
            }
        else:
            raise EnoException("Wrong variant_id provided")

    def getnoise(self):  # type: () -> None
        """
        This method retrieves noise in the service.
        The noise to be retrieved is inside self.flag
        The difference between noise and flag is, that noise does not have to remain secret for other teams.
        This method can be called many times per round. Check how often using variant_id.
        On error, raise an EnoException.
        :raises EnoException on error
        :return this function can return a result if it wants
                if nothing is returned, the service status is considered okay.
                the preferred way to report errors in the service is by raising an appropriate enoexception
        """
        if self.variant_id == 0:
            try:
                username: str = self.chain_db["username"]
                password: str = self.chain_db["password"]
                noteId: str = self.chain_db["noteId"]
                randomNote: str = self.chain_db["note"]
            except Exception as ex:
                self.debug("Failed to read db {ex}")
                raise BrokenServiceException("Previous putnoise failed.")

            self.debug(f"Connecting to service")
            conn = self.connect()
            welcome = conn.read_until(">")

            # Let's login to the service
            self.login_user(conn, username, password)

            # Let´s obtain our note.
            self.debug(f"Sending command to retrieve note: {noteId}")
            conn.write(f"get {noteId}\n")
            conn.readline_expect(
                randomNote.encode(),
                read_until=b">",
                exception_message="Resulting flag was found to be incorrect"
            )

            # Exit!
            self.debug(f"Sending exit command")
            conn.write(f"exit\n")
            conn.close()
        else:
            raise EnoException("Wrong variant_id provided")

    def havoc(self):  # type: () -> None
        """
        This method unleashes havoc on the app -> Do whatever you must to prove the service still works. Or not.
        On error, raise an EnoException.
        :raises EnoException on Error
        :return This function can return a result if it wants
                If nothing is returned, the service status is considered okay.
                The preferred way to report Errors in the service is by raising an appropriate EnoException
        """
        self.debug(f"Connecting to service")
        conn = self.connect()
        welcome = conn.read_until(">")

        if self.variant_id == 0:
            # In variant 1, we'll check if the help text is available
            self.debug(f"Sending help command")
            conn.write(f"help\n")
            is_ok = conn.read_until(">")

            for line in [
                "This is a notebook service. Commands:",
                "reg USER PW - Register new account",
                "log USER PW - Login to account",
                "set TEXT..... - Set a note",
                "user  - List all users",
                "list - List all notes",
                "exit - Exit!",
                "dump - Dump the database",
                "get ID",
            ]:
                assert_in(line.encode(), is_ok, "Received incomplete response.")

        elif self.variant_id == 1:
            # In variant 2, we'll check if the `user` command still works.
            username = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=12)
            )
            password = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=12)
            )

            # Register and login a dummy user
            self.register_user(conn, username, password)
            self.login_user(conn, username, password)

            self.debug(f"Sending user command")
            conn.write(f"user\n")
            ret = conn.readline_expect(
                "User 0: ",
                read_until=b">",
                exception_message="User command does not return any users",
            )

            if username:
                assert_in(username.encode(), ret, "Flag username not in user output")

        elif self.variant_id == 2:
            # In variant 2, we'll check if the `list` command still works.
            username = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=12)
            )
            password = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=12)
            )
            randomNote = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=36)
            )

            # Register and login a dummy user
            self.register_user(conn, username, password)
            self.login_user(conn, username, password)

            self.debug(f"Sending command to save a note")
            conn.write(f"set {randomNote}\n")
            conn.read_until(b"Note saved! ID is ")

            try:
                noteId = conn.read_until(b"!\n>").rstrip(b"!\n>").decode()
            except Exception as ex:
                self.debug(f"Failed to retrieve note: {ex}")
                raise BrokenServiceException("Could not retrieve NoteId")

            assert_equals(len(noteId) > 0, True, message="Empty noteId received")

            self.debug(f"{noteId}")

            self.debug(f"Sending list command")
            conn.write(f"list\n")
            conn.readline_expect(
                noteId.encode(),
                read_until=b'>',
                exception_message="List command does not work as intended"
            )

        else:
            raise EnoException("Wrong variant_id provided")

        # Exit!
        self.debug(f"Sending exit command")
        conn.write(f"exit\n")
        conn.close()

    def exploit(self):
        """
        This method was added for CI purposes for exploits to be tested.
        Will (hopefully) not be called during actual CTF.
        :raises EnoException on Error
        :return This function can return a result if it wants
                If nothing is returned, the service status is considered okay.
                The preferred way to report Errors in the service is by raising an appropriate EnoException
        """
        # TODO: We still haven't decided if we want to use this function or not. TBA
        pass


app = testifyChecker.service  # This can be used for uswgi.
if __name__ == "__main__":
    run(testifyChecker)
