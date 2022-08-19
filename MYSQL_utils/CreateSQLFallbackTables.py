from venv import create
from db_handler.mysql_dbconn import DbConnection 

conn = DbConnection()
for t in conn.get_table_names():
    if ("auth" in t or "django" in t or "drf" in t or "logs" in t):
            continue

    table = conn.get_table(t)
    columns = table.get_columns()

    primaryKey = ""

    for col in columns:
        if (col.key == "PRI"):
                  primaryKey = col.name

    create_table = conn.execute_and_fetch("SHOW CREATE TABLE ib_db.%s" % (t), 'one')[1]
    create_table = create_table.replace("utf8mb3", "utf8mb4")
    create_table = create_table.replace("`%s`"%(t), "`%s_history`"%(t))
    create_table = create_table.replace("`LastChangeBy` varchar(45) NOT NULL DEFAULT 'marc.aa',\n  ", "")
    create_table = create_table.replace("AUTO_INCREMENT,\n  ", "AUTO_INCREMENT,\n  `iLogs` int NOT NULL,\n  ")
    create_table = create_table.replace("%s"%(primaryKey), "%s_history"%(primaryKey))
    
    
    print(create_table)

    TR_INSERT = """
DELIMITER //
CREATE TRIGGER TR_%s_AfterInsert
	AFTER INSERT ON %s 
    FOR EACH ROW
BEGIN
    INSERT INTO `ib_db`.`logs`
    (`TableName`,
    `iTableID`,
    `Username`,
    `Date`,
    `Operation`)
    VALUES
    (/*TableName*/'%s',
    /*iTableID*/ NEW.%s,
    /*Username*/ NEW.LastChangeBy,
    /*Date*/ NOW(),
    /*Operation*/ 'INSERT');
END//
DELIMITER ;
    """ % (t, t, t, primaryKey)

    TR_UPDATE = """
DELIMITER //
CREATE TRIGGER TR_%s_AfterUpdate
	AFTER UPDATE ON %s 
    FOR EACH ROW
BEGIN
	DECLARE prmOperation varchar(15);
    
	if (OLD.Status = b'1' and NEW.Status = b'0') THEN
		SET prmOperation = 'SOFT DELETE';
	else
		SET prmOperation = 'UPDATE';
	END IF;
		
	INSERT INTO `ib_db`.`logs`
	(`TableName`,
	`iTableID`,
	`Username`,
	`Date`,
	`Operation`)
	VALUES
	(/*TableName*/'%s',
	/*iTableID*/ NEW.%s,
	/*Username*/ NEW.LastChangeBy,
	/*Date*/ NOW(),
	/*Operation*/ prmOperation);
END//
DELIMITER ;
    """ % (t, t, t, primaryKey)


    # print(TR_INSERT)
    print("")
    # print(TR_UPDATE)
    print("")
    print("")