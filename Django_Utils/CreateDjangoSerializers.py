from Django_Utils.CreateDjangoViews import DB_NAME
from db_handler.mysql_dbconn import DbConnection 

conn = DbConnection()
DB_NAME = conn.db_name

for t in conn.get_table_names():

    table = conn.get_table(t)
    columns = table.get_column_names()
    columns.pop(0)
    fields = conn.list_to_string(columns)

    caps_table_name = str(t[0:1]).upper() + str(t[1:]).lower()
    method = """class %sSerializer(serializers.ModelSerializer):
    	class Meta:
		model = %s
		fields = (%s)
    """ % (caps_table_name, caps_table_name, fields)

    text_file = open('DatabasesHelpers/' + DB_NAME + "/Django/serializers.txt", "w")
    text_file.write(method)
    text_file.close()