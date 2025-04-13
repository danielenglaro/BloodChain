CREATE DATABASE Users;

USE Users;

CREATE TABLE Users(
	Usrnm VARCHAR(200) UNIQUE,
    Pwd VARCHAR(200),
    PRIMARY KEY(Usrnm, Pwd)
)Engine= InnoDB;