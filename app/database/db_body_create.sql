CREATE TABLE User(
login VARCHAR(30),
hashed_password TEXT
);

CREATE TABLE Post(
id INT PRIMARY KEY AUTO_INCREMENT,
login VARCHAR(30) NOT NULL,
post TEXT NOT NULL,
date_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Love(
lover VARCHAR(30) NOT NULL,
loved VARCHAR(30) NOT NULL,
post_id INT,
date_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY(lover,post_id)
);

CREATE TABLE Login(
login VARCHAR(30),
date_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY(login, date_time)
);