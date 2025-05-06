DELIMITER //

CREATE TRIGGER cypher_ins_data BEFORE INSERT ON Ospedali
FOR EACH ROW 
BEGIN
    SET NEW.Usrnm = SHA2(CONCAT(NEW.Usrnm, 'Luca'), 512);
    SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, 'Luca'), 512);
END;
//

CREATE TRIGGER cypher_upd_data BEFORE UPDATE ON Ospedali
FOR EACH ROW 
BEGIN
    SET NEW.Usrnm = SHA2(CONCAT(NEW.Usrnm, 'Luca'), 512);
    SET NEW.Pwd = SHA2(CONCAT(NEW.Pwd, 'Luca'), 512);
END;
//

DELIMITER ;
