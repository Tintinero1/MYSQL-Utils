from db_handler.mysql_dbconn import DbConnection

def get_primary_key(columns:list):
    for column in columns:
        if column.key == "PRI":
            return column

def generate_sp_parameters(columns:list):
    """ Generates a string of SQL parameters
        I.E:
            IN prmName varchar(45),
            IN prmStatus varchar(20) 
        columns: list [
            {"name": "column_name", "type": "varchar(40)", "null": "YES/NO", "key": "PRI/empty_string"}, ...
        ]
    """
    sp_parameters = ""
    for prm in columns:
        comma = ","
        if (len(columns) == columns.index(prm)+1):
            comma = ""
        if prm.key != "PRI" and prm.extra != "auto_increment":
            sp_parameters += "IN prm%s %s%s\n" % (prm.name, prm.type, comma)

    return sp_parameters

def generate_columns_to_insert(columns:list, column_name_prefix:str=""):
    column_string = ""
    for col in columns:
        comma = ","
        if (len(columns) == columns.index(col)+1):
            comma = ""
        if col.key != "PRI" and col.extra != "auto_increment":
            column_string += "%s%s%s " % (column_name_prefix, col.name, comma)

    return column_string

def generate_columns_to_read(table_name, columns:list, column_name_prefix:str=""):
    column_string = ""
    for col in columns:
        comma = ","
        if (len(columns) == columns.index(col)+1):
            comma = ""

        if col.key != "PRI" and col.extra != "auto_increment" and col.name[0] != "i":
            if col.type == "bit(1)":
                column_string += "BIN(%s%s.%s) AS %s%s " % (column_name_prefix, table_name, col.name, col.name, comma)
            else:
                column_string += "%s%s.%s%s " % (column_name_prefix, table_name, col.name, comma)
            
        if col.name[0] == "i" and col.type == ("int") and col.key != "PRI":
            column_string += "%s%s.%sName%s " % (column_name_prefix, table_name, col.name[1:], comma)

    return column_string

def generate_read_where_clause(columns:list, operator="or"):
    column_string = ""
    for col in columns:
        if (len(columns) == columns.index(col)+1):
            operator = ""
        if col.key != "PRI" and col.extra != "auto_increment":
            column_string += "%s = prm%s %s " % (col.name, col.name, operator)

    return column_string

def generate_update_where_clause(columns:list, operator="or"):
    column_string = ""
    for col in columns:
        if (len(columns) == columns.index(col)+1):
            operator = ""
        if col.key != "PRI" and col.extra != "auto_increment":
            column_string += "ca.%s = prm%s %s " % (col.name, col.name, operator)

    return column_string

def generate_update_set_clause(columns:list):
    column_string = ""
    for col in columns:
        comma = ', '
        if (len(columns) == columns.index(col)+1):
            comma = ""
        if col.key != "PRI" and col.extra != "auto_increment":
            column_string += "%s = prmNEW%s%s" % (col.name, col.name, comma)

    return column_string

def create_stored_procedures():
    conn = DbConnection()
    tables = conn.get_table_names()
    generate_create_stored_procedures(tables)
    generate_read_stored_procedures(tables)
    generate_update_stored_procedures(tables)
    generate_soft_delete_stored_procedures(tables)
    generate_scan_stored_procedures(tables)


def generate_create_stored_procedures(tables:list):
    conn = DbConnection()
    for table in tables:
        sp_name = 'spCreate' + table
        if("auth" in sp_name or "django" in sp_name or "_history" in sp_name):
            continue
        t = conn.get_table(table)
        columns = t.get_columns()
        column_names = generate_columns_to_insert(columns)
        column_values = generate_columns_to_insert(columns, 'prm')
        column_values = column_values.replace("prmStatus", "cast_to_bit(prmStatus)")
        sp_parameters = generate_sp_parameters(columns)
        primary_key = get_primary_key(columns)
        DB_NAME = conn.db_name
        
        sp_skeleton = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `%s`(
    %s
)
BEGIN

DECLARE idRecordExists INT DEFAULT 0;

SET idRecordExists = IFNULL((select %s from YOUR_DATABASE_NAME_HERE.%s as %s where %s.%s = prm%s),0);
if idRecordExists = '0' THEN
    INSERT INTO `YOUR_DATABASE_NAME_HERE`.`%s`
    (%s)
    VALUES
    (%s);
END IF;

END
""" % (sp_name, sp_parameters, primary_key.name, table, table[0], table[0], columns[1].name, columns[1].name, table, column_names, column_values)

        sp_skeleton = sp_skeleton.replace("prmStatus bit(1)", "prmStatus INT")
        sp_skeleton = sp_skeleton.replace("YOUR_DATABASE_NAME_HERE", DB_NAME)
        text_file = open('DatabasesHelpers/' + DB_NAME + '/SP/CREATE/' + sp_name + ".txt", "w")
        text_file.write(sp_skeleton)
        text_file.close()

def generate_read_stored_procedures(tables:list):
    conn = DbConnection()
    for table in tables:
        sp_name = 'spRead' + table
        if("auth" in sp_name or "django" in sp_name or "_history" in sp_name):
            continue
        t = conn.get_table(table)
        columns = t.get_columns()
        column_names = generate_columns_to_read(table, columns)
        column_values = generate_columns_to_insert(columns, 'prm')
        sp_parameters = generate_sp_parameters(columns)
        read_where_clause = generate_read_where_clause(columns, operator='or')
        DB_NAME = conn.db_name

        INNER_JOINS = ""
        INNER_JOINS_COUNTER = 1

        for col in columns:
            if col.name[0] == "i" and col.type == ("int") and col.key != "PRI":
                INNER_JOINS += """
INNER JOIN TABLE_NAME as t%s
on t%s.%s = %s.%s""" % (str(INNER_JOINS_COUNTER), str(INNER_JOINS_COUNTER), col.name, table, col.name)
                INNER_JOINS_COUNTER += 1

        
        sp_skeleton = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `%s`(
    %s
)
BEGIN

select %s from YOUR_DATABASE_NAME_HERE.%s 
%s
where %s;

END
""" % (sp_name, sp_parameters, column_names, table, INNER_JOINS, read_where_clause)

        sp_skeleton = sp_skeleton.replace("prmStatus bit(1)", "prmStatus INT")
        sp_skeleton = sp_skeleton.replace("YOUR_DATABASE_NAME_HERE", DB_NAME)
        text_file = open('DatabasesHelpers/' + DB_NAME + '/SP/READ/' + sp_name + ".txt", "w")
        text_file.write(sp_skeleton)
        text_file.close()

def generate_update_stored_procedures(tables:list):
    conn = DbConnection()
    for table in tables:
        sp_name = 'spUpdate' + table
        if("auth" in sp_name or "django" in sp_name or "_history" in sp_name):
            continue
        t = conn.get_table(table)
        columns = t.get_columns()
        column_names = generate_columns_to_insert(columns)
        column_values = generate_columns_to_insert(columns, 'prm')
        sp_parameters = generate_sp_parameters(columns)
        sp_NEWparameters = sp_parameters.replace("prm", "prmNEW")
        sp_parameters = sp_parameters.replace("IN prmLastChangeBy varchar(45)", "")
        primary_key = get_primary_key(columns)
        set_clause = generate_update_set_clause(columns)
        DB_NAME = conn.db_name
        
        DECLARE_VARIABLES = ""
        NEW_DECLARE_VARIABLES = ""
        DECLARE_PK_ID = ""
        SET_VARS = ""
        SET_NEWVARS = ""
        RECORD_UPDATE_WHERE_CLAUSE = generate_update_where_clause(columns, "and")

        validate_active_record = ""
        for col in columns:
            if col.name.lower() == "Status".lower():
                validate_active_record = "and %s.%s = INACTIVO" % (table, col.name)
            if col.name[0] == "i" and col.type == ("int") and col.key != "PRI":
                DECLARE_VARIABLES += "DECLARE VAR_%s INT DEFAULT 0;\n" % (col.name)
                NEW_DECLARE_VARIABLES += "DECLARE NEWVAR_%s INT DEFAULT 0;\n" % (col.name)
                SET_VARS += "SET VAR_%s = IFNULL((select %s from ib_db.PUT_TABLE_HERE as con where con.%s = %s),0);\n" % (col.name, col.name, col.name[1:] + "Name", "prm" + col.name[1:] + "Name")
                SET_NEWVARS += "SET NEWVAR_%s = IFNULL((select %s from ib_db.PUT_TABLE_HERE as con where con.%s = %s),0);\n" % (col.name, col.name, col.name[1:] + "Name", "prmNEW" + col.name[1:] + "Name")
            if col.key == "PRI":
                DECLARE_PK_ID += "DECLARE id%s INT DEFAULT 0;" % (col.name)

        RECORD_UPDATE = """
SET id%s = IFNULL((select %s from ib_db.%s as ca where %s),0);
        """ % (primary_key.name, primary_key.name, table, RECORD_UPDATE_WHERE_CLAUSE)

        NEW_RECORD_UPDATE = RECORD_UPDATE.replace("prm", "prmNEW")
        NEW_RECORD_UPDATE = NEW_RECORD_UPDATE.replace("id%s" %(primary_key.name), "idRecordExists")


        
        sp_skeleton = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `%s`(
    %s%s
)
BEGIN

DECLARE idRecordExists INT DEFAULT 0;

%s

%s
%s

-- Set id's by name
%s
-- Set new id's by name
%s
-- Set id of record to update
%s
-- Check if record exists with the new info
%s

if id%s <> '0' and idRecordExists = '0' THEN
    UPDATE YOUR_DATABASE_NAME_HERE.%s
	SET %s
	WHERE id%s = %s; 
END IF;

END
""" % (sp_name, sp_parameters, sp_NEWparameters, DECLARE_VARIABLES, NEW_DECLARE_VARIABLES, DECLARE_PK_ID, SET_VARS, SET_NEWVARS, RECORD_UPDATE, NEW_RECORD_UPDATE, primary_key.name, table, set_clause, primary_key.name, primary_key.name)

        sp_skeleton = sp_skeleton.replace("prmStatus bit(1)", "prmStatus INT")
        sp_skeleton = sp_skeleton.replace("YOUR_DATABASE_NAME_HERE", DB_NAME)
        text_file = open('DatabasesHelpers/' + DB_NAME + '/SP/UPDATE/' + sp_name + ".txt", "w")
        text_file.write(sp_skeleton)
        text_file.close()

def generate_soft_delete_stored_procedures(tables:list):
    conn = DbConnection()
    for table in tables:
        sp_name = 'spSoftDelete' + table
        if("auth" in sp_name or "django" in sp_name or "_history" in sp_name):
            continue
        t = conn.get_table(table)
        columns = t.get_columns()
        column_names = generate_columns_to_insert(columns)
        column_values = generate_columns_to_insert(columns, 'prm')
        sp_parameters = generate_sp_parameters(columns)
        primary_key = get_primary_key(columns)
        DB_NAME = conn.db_name

        status_column = ""
        for col in columns:
            if col.name.lower() == "Status".lower():
                status_column = "%s.%s" % (table, col.name)

        
        sp_skeleton = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `%s`(
    %s
)
BEGIN

DECLARE idRecordExists INT DEFAULT 0;

SET idRecordExists = IFNULL((select %s from YOUR_DATABASE_NAME_HERE.%s as %s where %s.%s = prm%s),0);
if idRecordExists <> '0' THEN
    UPDATE YOUR_DATABASE_NAME_HERE.%s
	SET %s = INACTIVO
	WHERE idRecordExists = %s; 
END IF;

END
""" % (sp_name, sp_parameters, primary_key.name, table, table[0], table[0], columns[1].name, columns[1].name, table, status_column, primary_key.name)

        sp_skeleton = sp_skeleton.replace("prmStatus bit(1)", "prmStatus INT")
        sp_skeleton = sp_skeleton.replace("YOUR_DATABASE_NAME_HERE", DB_NAME)
        text_file = open('DatabasesHelpers/' + DB_NAME + '/SP/SOFT_DELETE/' + sp_name + ".txt", "w")
        text_file.write(sp_skeleton)
        text_file.close()

def generate_scan_stored_procedures(tables:list):
    conn = DbConnection()
    for table in tables:
        sp_name = 'spScan' + table
        if("auth" in sp_name or "django" in sp_name or "_history" in sp_name):
            continue
        t = conn.get_table(table)
        columns = t.get_columns()
        column_names = generate_columns_to_read(table, columns)
        column_values = generate_columns_to_insert(columns, 'prm')
        sp_parameters = generate_sp_parameters(columns)
        primary_key = get_primary_key(columns)
        DB_NAME = conn.db_name

        status_column = ""
        INNER_JOINS = ""
        INNER_JOINS_COUNTER = 1

        for col in columns:
            if col.name.lower() == "Status".lower():
                status_column = "%s.%s" % (table, col.name)
            if col.name[0] == "i" and col.type == ("int") and col.key != "PRI":
                INNER_JOINS += """
INNER JOIN TABLE_NAME as t%s
on t%s.%s = %s.%s""" % (str(INNER_JOINS_COUNTER), str(INNER_JOINS_COUNTER), col.name, table, col.name)
                INNER_JOINS_COUNTER += 1

        
        sp_skeleton = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `%s`(
	IN prmStatus INT
)
BEGIN

SELECT %s
from %s
%s
WHERE %s.Status = cast_to_bit(prmStatus);

END
""" % (sp_name, column_names, table, INNER_JOINS, table)

        sp_skeleton = sp_skeleton.replace(", LastChangeBy", "")
        text_file = open('DatabasesHelpers/' + DB_NAME + '/SP/SCAN/' + sp_name + ".txt", "w")
        text_file.write(sp_skeleton)
        text_file.close()


if __name__ == "__main__":
    create_stored_procedures()
    print("Sp's created at " + 'DatabasesHelpers/')
