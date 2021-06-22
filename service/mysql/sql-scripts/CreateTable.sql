CREATE TABLE users (
	user_id INT NOT NULL AUTO_INCREMENT,
	username VARCHAR(30) NOT NULL UNIQUE,
	password BINARY(32) NOT NULL,
	salt BINARY(32) NOT NULL,
	email VARCHAR(255) UNIQUE NOT NULL,
	is_doctor BOOLEAN NOT NULL DEFAULT 0,
	PRIMARY KEY (user_id)
);

CREATE TABLE sessions (
    session_id VARCHAR(36) NOT NULL,
    user_id INT,
    PRIMARY KEY (session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE appointments (
    appointment_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    extra_info VARCHAR(500),
    date DATETIME NOT NULL,
    filename VARCHAR(128),
    doctor VARCHAR(30),
    PRIMARY KEY (appointment_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

REVOKE ALL PRIVILEGES, GRANT OPTION FROM usertable_user;
GRANT SELECT ON user_database.users to usertable_user@'%';
ALTER USER 'usertable_user'@'%' IDENTIFIED WITH mysql_native_password BY 'userpass';