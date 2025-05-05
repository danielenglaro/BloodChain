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

CREATE TRIGGER cypher_ins_data BEFORE INSERT ON Ospedale
FOR EACH ROW 
    BEGIN
        -- Concatenare il salt fisso alla password/nome utente prima di fare l'hash
        SET NEW.Usrnm = SHA2(CONCAT(NEW.Usrnm, @salt), 512);
        SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, @salt), 512);
        -- Se vuoi memorizzare anche il salt, puoi aggiungere una colonna per esso (opzionale)
        -- SET NEW.Salt = @salt;
    END;//

CREATE TRIGGER cypher_upd_data BEFORE UPDATE ON Ospedale
FOR EACH ROW 
    BEGIN        
        -- Concatenare il salt fisso alla password/nome utente prima di fare l'hash
        SET NEW.Usrnm = SHA2(CONCAT(NEW.Usrnm, @salt), 512);
        SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, @salt), 512);
        -- Se vuoi memorizzare anche il salt, puoi aggiungere una colonna per esso (opzionale)
        -- SET NEW.Salt = @salt;
    END;//

DELIMITER ;
