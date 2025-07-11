DELIMITER //

CREATE TRIGGER cypher_ins_data BEFORE INSERT ON Ospedali
FOR EACH ROW 
BEGIN
    SET NEW.Usrnm = SHA2(CONCAT(NEW.Usrnm, 'Luca'), 512);
    SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, 'Luca'), 512);
END;
//

CREATE TRIGGER cypher_upd_data
BEFORE UPDATE ON Ospedali
FOR EACH ROW 
BEGIN
    -- Codifica username solo se è cambiato
    IF NOT (NEW.Usrnm <=> OLD.Usrnm) THEN
        SET NEW.Usrnm = SHA2(CONCAT(NEW.Usrnm, 'Luca'), 512);
    END IF;

    -- Codifica password solo se è cambiata
    IF NOT (NEW.Pwd <=> OLD.Pwd) THEN
        SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, 'Luca'), 512);
    END IF;
END;
//


DELIMITER ;

DELIMITER //

CREATE TRIGGER cypher_ins_data_d BEFORE INSERT ON Donatori
FOR EACH ROW 
BEGIN
    SET NEW.CF = SHA2(CONCAT(NEW.CF, 'Luca'), 512);
    SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, 'Luca'), 512);
END;
//

CREATE TRIGGER cypher_upd_data_d
BEFORE UPDATE ON Donatori
FOR EACH ROW 
BEGIN
    -- Codifica username solo se è cambiato
    IF NOT (NEW.CF <=> OLD.CF) THEN
        SET NEW.CF = SHA2(CONCAT(NEW.CF, 'Luca'), 512);
    END IF;

    -- Codifica password solo se è cambiata
    IF NOT (NEW.Pwd <=> OLD.Pwd) THEN
        SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, 'Luca'), 512);
    END IF;
END;
//


DELIMITER ;
DELIMITER //

CREATE PROCEDURE LoginOspedaleHash(
    IN p_username VARCHAR(255),
    IN p_password VARCHAR(255),
    OUT p_id BIGINT
)
BEGIN
    SELECT Id INTO p_id
    FROM Ospedali
    WHERE Usrnm = SHA2(CONCAT(p_username, 'Luca'), 512)
      AND Pwd = SHA2(CONCAT(p_password, 'Luca'), 512)
    LIMIT 1;

    IF p_id IS NULL THEN
        SET p_id = -1;
    END IF;
END;
//

DELIMITER ;
DELIMITER //

CREATE FUNCTION HashWithSalt(data VARCHAR(200))
RETURNS VARCHAR(200) DETERMINISTIC
BEGIN
    DECLARE hash VARCHAR(200);
    SET hash = (SHA2(CONCAT(data, 'Luca'), 512));
    RETURN hash;
END;
//
DELIMITER ;