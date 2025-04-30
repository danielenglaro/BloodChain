CREATE DATABASE BloodBase;

USE BloodBase;

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

CREATE TABLE Dati_Ospedali(
    Nome VARCHAR(200),
    Codice INT(200),
    PartitaIVA VARCHAR(200),
    Indirizzo VARCHAR(200),
    Coordinate FLOAT(200),
    Regione VARCHAR(200),
    Comune VARCHAR(200),
    Telefono INT(10),
    SitoWeb VARCHAR(200),
    PRIMARY KEY(Nome)
)Engine= InnoDB;