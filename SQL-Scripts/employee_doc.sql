DROP TABLE IF EXISTS users;

CREATE TABLE users(
	id SERIAL,
	email varchar(200) DEFAULT NULL,
	username varchar(45) DEFAULT NULL,
	first_name varchar(45) DEFAULT NULL,
	last_name varchar(45) DEFAULT NULL,
	hashed_password varchar(200) DEFAULT NULL,
	is_active boolean DEFAULT NULL,
	PRIMARY KEY (id)
);

DROP TABLE IF EXISTS tasks;

CREATE TABLE tasks(
	id SERIAL,
	task_name varchar(200) DEFAULT NULL,
	task_category varchar(80) DEFAULT NULL,
	date_taken DATE,
	owner_id integer DEFAULT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users(id)
);