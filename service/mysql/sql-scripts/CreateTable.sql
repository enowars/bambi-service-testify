CREATE TABLE users (
	user_id INT NOT NULL AUTO_INCREMENT,
	username VARCHAR(256) NOT NULL UNIQUE,
	password BINARY(32) NOT NULL,
	salt BINARY(32) NOT NULL,
	email VARCHAR(256) UNIQUE NOT NULL,
	is_doctor BOOLEAN NOT NULL DEFAULT 0,
	creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_id)
);

CREATE TABLE sessions (
	session_id VARCHAR(36) NOT NULL,
	user_id INT NOT NULL,
	PRIMARY KEY (session_id),
	CONSTRAINT fk_session_user_id FOREIGN KEY (user_id) REFERENCES users(user_id)
		ON DELETE CASCADE
);

CREATE TABLE appointments (
	appointment_id INT NOT NULL AUTO_INCREMENT,
	user_id INT NOT NULL,
	name VARCHAR(100) NOT NULL,
	extra_info VARCHAR(500),
	date DATETIME NOT NULL,
	filename VARCHAR(128),
	doctor VARCHAR(256),
	pin VARCHAR(30) NOT NULL,
	PRIMARY KEY (appointment_id),
	CONSTRAINT fk_appointments_user_id FOREIGN KEY (user_id) REFERENCES users(user_id)
		ON DELETE CASCADE
);

REVOKE ALL PRIVILEGES, GRANT OPTION FROM usertable_user;
GRANT SELECT ON user_database.users to usertable_user@'%';
ALTER USER 'usertable_user'@'%' IDENTIFIED WITH mysql_native_password BY 'userpass';

SET GLOBAL event_scheduler = ON;
CREATE EVENT cleaning ON SCHEDULE EVERY 10 MINUTE ENABLE
	DO DELETE FROM users WHERE users.username NOT LIKE 'doctor0_'
		AND users.creation_time < CURRENT_TIMESTAMP - INTERVAL 20 MINUTE;

