Testify Service documentation
======================

Service for making appointments with patients and doctors.

# Exploits

View `checker/src/checker.py` for a sample implementation.

## VULN #1:

1. Make an appointment with the filename `..<TARGET-USERNAME>-info.txt`.
The service will prefix your username to the filename
`<YOUR-USERNAME>-..<TARGET-USERNAME>-info.txt` and then split by `..`,
keeping the last part, and remove any `/`, resulting in `<TARGET-USERNAME>-info.txt`
placed in the database.

2. Retrieve the ID file for the service and this will return the info file
including the flag, saved at `<TARGET-USERNAME>-info.txt`.


## VULN #2:

1. Create appointment with a new user

2. Make an appointment and indicate the current user as the doctor
(modify POST request)

3. Access the `/doctors` page to retrieve the info for other users as
the `check_doctor` function in `testify.py` determines if a user is a
doctor by checking if they were appointed as doctor in any appointment.
The flag is stored in the user note for the doctor.

