CREATE DATABASE Users;

USE Users;

CREATE TABLE Donatori(
    CF VARCHAR(200),
    Pwd VARCHAR(200),
    
    PRIMARY KEY(CF, Pwd)
)Engine= InnoDB;

CREATE TABLE Ospedali(
    Username VARCHAR(200),
    Pwd VARCHAR(200),

    PRIMARY KEY(Username, Pwd)
)Engine= InnoDB;
