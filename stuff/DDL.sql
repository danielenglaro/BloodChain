CREATE DATABASE Users;

USE Users;

CREATE TABLE Donatori(
    CF VARCHAR(200),
    Pwd VARCHAR(200),
    PRIMARY KEY(CF, Pwd)
)Engine= InnoDB;

CREATE TABLE Ospedali(
    Usrnm VARCHAR(200) UNIQUE,
    Pwd VARCHAR(200),
    Id INT,
    PRIMARY KEY(Usrnm, Pwd)
)Engine= InnoDB;

CREATE VIEW stat_osp AS
SELECT Ospedali.Id, Ospedali.Sacche, SaccheTotali() AS SaccheTot FROM Ospedali;