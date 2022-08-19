from mysql.connector import connect

class DbConnection(object):

    mydb = ""
    __instance = None

    def __new__(cls):
        """ Singleton model for Database """
        if DbConnection.__instance is None:
            DbConnection.__instance = object.__new__(cls)
        
        return DbConnection.__instance

    def __init__(self, host="localhost", user="root", passwd="Monotiti1", db_name="ib_db"):
            self.db_name = db_name
            self.mydb = connect(host=host, user=user, passwd=passwd, auth_plugin='mysql_native_password')

    def list_to_string(self, items):
        """ Converts a list to a string with commas\n
        [a, b, c] = 'a, b, c'"""
        return ', '.join(items)

    def list_to_string_with_quotes(self, items:list):
        """ Converts a list to a string with commas\n
        [a, b, c] = 'a', 'b', 'c'"""
        result = ""
        comma = ','
        for item in items:
            if (len(items) == items.index(item)+1):
                comma = ''
            result += "'%s'%s" % (item, comma)
        return result
    
    def execute_and_fetch(self, query, fetch='all'):
        """ Opens up a cursor and closes it automatically after executing a desired query\n
        Returns result \n
        fetch: str: 'all', 'one', 'many', 'none'"""
        try:
            self.cursor = self.mydb.cursor()
            self.cursor.execute("use %s" % (self.db_name))
            self.cursor.execute(query)
            if fetch == 'one':
                result = self.cursor.fetchone()
            elif fetch == 'all':
                result = self.cursor.fetchall()
            elif fetch == 'many':
                result = self.cursor.fetchmany()
            else:
                result = []
            return result
        except Exception as e:
            print(e)
        finally:
            if (self.mydb.is_connected()):
                self.cursor.close()

    def get_table_names(self):
        """ Returns a list of table strings: ['table 1', 'table 2', ...]"""
        tables = []
        result = self.execute_and_fetch('SHOW TABLES')
        
        for table_name in result:
            tables.append(table_name[0].decode())
        
        return tables

    def get_table(self, table_name:str):
        """ Returns a Table Object with the specified table name """
        return self.Table(table_name, self);

    def get_stored_procedure(self, sp_name:str):
        """ Returns a StoredProcedure object with the specified sp name 
        :param str sp_name: name of Stored Procedure"""
        return self.StoredProcedure(sp_name, self);

    def get_stored_procedures(self):
        """ Returns a all StoredProcedure objects in Database 
        [ StoredProcedure(sp_name), ... ]"""

        result = self.execute_and_fetch("""
            SHOW PROCEDURE STATUS WHERE Db = '%s';
        """ % (self.db_name), 'all')

        stored_procedures = []

        for sp in result:
            stored_procedure = self.StoredProcedure(
                sp_name = sp[1],
                _parent = self
            )

            stored_procedures.append(stored_procedure)
        return stored_procedures

    def call_sp(self, sp_name:str, fetch='all', *args):
        """ Calls a SP from database with it's arguments
        :param str sp_name: name of Stored Procedure 
        :param str fetch: fetch result mode 'all','one','many','none'
        :param str *args: parameters for stored procedure
        :return: stored procedure results"""
        try:
            cursor = self.mydb.cursor()
            cursor.execute("USE {}".format(self.db_name))
            cursor.callproc(sp_name, args)
            self.mydb.commit()

            result = list(cursor.stored_results())
            if len(result) == 0:
                return []
            elif len(result) >= 1:
                result = result[0]
            
            if fetch == 'one':
                return result.fetchone()
            elif fetch == 'all':
                return result.fetchall()
            elif fetch == 'many':
                return result.fetchmany()
            else:
                return []
        except Exception as e:
            print("Failed to execute Stored Procedure: {}".format(e))
        finally:
            if (self.mydb.is_connected()):
                cursor.close()
        

    


    class Table():

        def __init__(self, table_name:str, _parent):
            self.table_name = table_name
            self.parent = _parent


        def get_columns(self):
            """ Returns a list of all column objects in Table \n
            [ Column(name, type, null, key, defualt, extra), ... ]"""
            columns = []
            
            result = self.parent.execute_and_fetch("SHOW COLUMNS FROM %s.%s" % (self.parent.db_name, self.table_name))

            for column in result:
                col = self.Column(
                    name= column[0],
                    type = column[1].decode(),
                    null = column[2],
                    key = column[3].decode(),
                    default = column[4],
                    extra = column[5]
                )

                columns.append(col)
            return columns

        def get_column_names(self):
            """ Returns a list of column strings: ['column 1', 'column 2', ...]"""
            columns = self.get_columns()
            column_names = []
            for col in columns:
                column_names.append(col.name)
            return column_names

        class Column():
            def __init__(self, name, type, null, key, default, extra):
                self.name = name
                self.type = type
                self.null = null
                self.key = key
                self.default = default
                self.extra = extra

    class StoredProcedure():

        def __init__(self, sp_name:str, _parent):
            self.sp_name = sp_name
            self.parent = _parent

        def get_parameters(self):
            """ Returns a list of all parameters in the Stored Procedure object \n
            [ Parameter(specific_name, ordinal_position, parameter_mode, parameter_name, data_type, character_maximum_length)]"""
            parameters = []

            result = self.parent.execute_and_fetch("""
                SELECT SPECIFIC_NAME, ORDINAL_POSITION, PARAMETER_MODE, PARAMETER_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                FROM information_schema.parameters 
                WHERE SPECIFIC_NAME = '%s';
            """ % (self.sp_name))

            for parameter in result:
                prm = self.Parameter(
                    specific_name = parameter[0],
                    ordinal_position = parameter[1],
                    parameter_mode = parameter[2],
                    parameter_name = parameter[3],
                    data_type = parameter[4],
                    character_maximum_length = parameter[5]
                )

                parameters.append(prm)
            return parameters

        def get_parameter_names(self):
            """ Returns a list of parameter strings: ['parameter 1', 'parameter 2', ...]"""
            parameters = self.get_parameters()
            parameter_names = []
            for prm in parameters:
                parameter_names.append(prm.parameter_name)
            return parameter_names

        class Parameter():
            def __init__(self, specific_name, ordinal_position, parameter_mode, parameter_name, data_type, character_maximum_length):
                self.specific_name = specific_name
                self.ordinal_position = ordinal_position
                self.parameter_mode = parameter_mode
                self.parameter_name = parameter_name
                self.data_type = data_type
                self.character_maximum_length = character_maximum_length