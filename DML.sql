DELIMITER //

CREATE TRIGGER cypher_ins_data BEFORE INSERT ON Users
FOR EACH ROW 
    BEGIN
        -- Definisci un salt fisso
        SET @salt = 'Luca';
        
        -- Concatenare il salt fisso alla password/nome utente prima di fare l'hash
        SET NEW.Usrnm = SHA2(CONCAT(NEW.Usrnm, @salt), 512);
        SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, @salt), 512);
        
        -- Se vuoi memorizzare anche il salt, puoi aggiungere una colonna per esso (opzionale)
        -- SET NEW.Salt = @salt;
    END;//

CREATE TRIGGER cypher_upd_data BEFORE UPDATE ON Users
FOR EACH ROW 
    BEGIN
        -- Definisci un salt fisso
        SET @salt = 'Luca';
        
        -- Concatenare il salt fisso alla password/nome utente prima di fare l'hash
        SET NEW.Usrnm = SHA2(CONCAT(NEW.Usrnm, @salt), 512);
        SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, @salt), 512);
        
        -- Se vuoi memorizzare anche il salt, puoi aggiungere una colonna per esso (opzionale)
        -- SET NEW.Salt = @salt;
    END;//

DELIMITER ;
