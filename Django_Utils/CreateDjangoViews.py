from db_handler.mysql_dbconn import DbConnection 

conn = DbConnection()
DB_NAME = conn.db_name

views_result = ""

for t in conn.get_table_names():
      if ("auth" in t or "django" in t):
            continue
      
      caps_table_name = str(t[0:1]).upper() + str(t[1:]).lower()
      table = conn.get_table(t)
      columns = table.get_column_names()
      firstVar = columns[1]
      ColumnObjects = table.get_columns()

      # CREATE_PARAMS
      sp_create = conn.get_stored_procedure("spCreate%s" % (t))
      sp_create_parameters = sp_create.get_parameters()
      POST_PARAMETER_NAMES = sp_create.get_parameter_names()

      # READ_PARAMS
      sp_read = conn.get_stored_procedure("spRead%s" % (t))
      sp_read_parameters = sp_read.get_parameters()
      GET_PARAMETER_NAMES = sp_read.get_parameter_names()

      # UPDATE_PARAMS
      sp_update = conn.get_stored_procedure("spUpdate%s" % (t))
      sp_update_parameters = sp_update.get_parameters()
      PUT_PARAMETER_NAMES = sp_update.get_parameter_names()

      # SCAN_PARAMS
      sp_scan = conn.get_stored_procedure("spScan%s" % (t))
      sp_scan_parameters = sp_scan.get_parameters()
      SCAN_PARAMETER_NAMES = sp_scan.get_parameter_names()


      # REQUESTS
      POST_PARAMS = ""
      for prm in sp_create_parameters:
            POST_PARAMS += "%s = data['%s']\n    " % (prm.parameter_name.replace("prm",""), prm.parameter_name.replace("prm",""))

      GET_PARAMS = ""
      for prm in sp_read_parameters:
            GET_PARAMS += "%s = request.query_params.get('%s')\n    " % (prm.parameter_name.replace("prm",""), prm.parameter_name.replace("prm",""))

      PUT_PARAMS = ""
      for prm in sp_update_parameters:
            PUT_PARAMS += "%s = data['%s']\n    " % (prm.parameter_name.replace("prm",""), prm.parameter_name.replace("prm",""))

      SCAN_PARAMS = ""
      for prm in sp_scan_parameters:
            SCAN_PARAMS += "%s = request.query_params.get('%s')\n    " % (prm.parameter_name.replace("prm",""), prm.parameter_name.replace("prm",""))
      

      POST_PARAMETER_NAMES = str(POST_PARAMETER_NAMES).replace("'", "").replace("prm","")
      GET_PARAMETER_NAMES = str(GET_PARAMETER_NAMES).replace("'", "").replace("prm","")
      PUT_PARAMETER_NAMES = str(PUT_PARAMETER_NAMES).replace("'", "").replace("prm","")
      SCAN_PARAMETER_NAMES = str(SCAN_PARAMETER_NAMES).replace("'", "").replace("prm","")


      method_POST = """
@api_view(['POST'])
def %sCreate(request):
    data = request.data
    %s
    conn = DbConnection()
    conn.call_sp('spCreate%s', 'one', *%s)
    return Response(request.data)
      """ % (t, POST_PARAMS, t, POST_PARAMETER_NAMES)
      
      method_GET = """
@api_view(['GET'])
def %sRead(request):
    %s
    conn = DbConnection()
    params = %s
    result = conn.call_sp('spRead%s', 'all', *params)
    return Response(result)
      """ % (t, GET_PARAMS, GET_PARAMETER_NAMES, t)

      method_PUT = """
@api_view(['PUT'])
def %sUpdate(request):
    data = request.data
    %s
    conn = DbConnection()
    conn.call_sp('spUpdate%s', 'one', *%s)
    return Response(request.data)
      """ % (t, PUT_PARAMS, t, PUT_PARAMETER_NAMES)

      method_DELETE = """
@api_view(['DELETE'])
def %sRead(request):
    %s = request.query_params.get('%s')
    conn = DbConnection()
    params = [%s]
    result = conn.call_sp('spRead%s', 'one', *params)
    return Response('Deleted ' + %s)
      """ % (t, firstVar, firstVar, firstVar, t, firstVar)

      method_SCAN = """
@api_view(['GET'])
def %sScan(request):
    %s
    conn = DbConnection()
    params = %s
    result = conn.call_sp('spScan%s', 'all', *params)
    return Response(result)
      """ % (t, SCAN_PARAMS, SCAN_PARAMETER_NAMES, t)
      
      views_result += "# " + t + "\n" + method_POST + method_GET + method_PUT + method_SCAN + "\n\n"

text_file = open('DatabasesHelpers/' + DB_NAME + '/Django/' + "views.txt", "w")
text_file.write(views_result)
text_file.close()

print("Views created at " + 'DatabasesHelpers/' + DB_NAME + '/Django/')