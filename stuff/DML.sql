SET @salt = 'Luca';

CREATE TRIGGER cypher_ins_dati_Ospedale BEFORE INSERT ON Ospedali
FOR EACH ROW
BEGIN
    SET NEW.codice_identificativo = SHA2(CONCAT(NEW.codice_identificativo, @salt), 512);
    SET NEW.partita_iva = SHA2(CONCAT(NEW.partita_iva, @salt), 512);
    SET NEW.gps = SHA2(CONCAT(NEW.gps, @salt), 512);
    SET NEW.telefono = SHA2(CONCAT(NEW.telefono, @salt), 512);
    SET NEW.sito_web = SHA2(CONCAT(NEW.sito_web, @salt), 512);
END;

CREATE TRIGGER cypher_ins_Donatori BEFORE INSERT ON Donatori
FOR EACH ROW
    BEGIN
        SET NEW.CF = SHA2(CONCAT(NEW.CF, @salt), 512);
        SET NEW.password = SHA2(CONCAT(NEW.password, @salt), 512);
    END;

CREATE TRIGGER cypher_ins_Ospedali BEFORE INSERT ON Ospedali
FOR EACH ROW
    BEGIN
        SET NEW.username = SHA2(CONCAT(NEW.username, @salt), 512);
        SET NEW.password = SHA2(CONCAT(NEW.password, @salt), 512);9
    END;
