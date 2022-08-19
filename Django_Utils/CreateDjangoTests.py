from db_handler.mysql_dbconn import DbConnection 

conn = DbConnection()
DB_NAME = conn.db_name

CREATEresult = ""
READresult = ""
UPDATEresult = ""
SCANresult = ""
result = ""

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

      # READ_PARAMS
      sp_read = conn.get_stored_procedure("spRead%s" % (t))
      sp_read_parameters = sp_read.get_parameters()

      # UPDATE_PARAMS
      sp_update = conn.get_stored_procedure("spUpdate%s" % (t))
      sp_update_parameters = sp_update.get_parameters()

      # SCAN_PARAMS
      sp_scan = conn.get_stored_procedure("spScan%s" % (t))
      sp_scan_parameters = sp_scan.get_parameters()


      # REQUESTS
      CREATEparams = ""
      for prm in sp_create_parameters:
            CREATEparams += '"%s": "",\n            ' % (prm.parameter_name)
      CREATEparams = CREATEparams.replace("prm","")

      READparams = ""
      for prm in sp_read_parameters:
            READparams += '"%s": "",\n            ' % (prm.parameter_name)
      READparams = READparams.replace("prm","")

      UPDATEparams = ""
      for prm in sp_update_parameters:
            UPDATEparams += '"%s": "",\n            ' % (prm.parameter_name)
      UPDATEparams = UPDATEparams.replace("prm","")

      SCANparams = ""
      for prm in sp_scan_parameters:
            SCANparams += '"%s": "",\n            ' % (prm.parameter_name)
      SCANparams = SCANparams.replace("prm","")
      

      READ_TESTS = """
def test_%s_read():
      params = {
            %s
      }
      r = requests.get(APP_URL + '%s-read/', params=params)
      print(json.loads(r.content))
      if type(json.loads(r.content)) == type(list()):
            return print("Ok")

      """ % (t, READparams, t)

      CREATE_TESTS = """
def test_%s_create():
      params = {
            %s
      }
      r = requests.post(APP_URL + '%s-create/', data=params)
      print(json.loads(r.content))
      if type(json.loads(r.content)) == type(list()):
            return print("Ok")

      """ % (t, CREATEparams, t)

      UPDATE_TESTS = """
def test_%s_update():
      params = {
            %s
      }
      r = requests.put(APP_URL + '%s-update/', data=params)
      print(json.loads(r.content))
      if type(json.loads(r.content)) == type(list()):
            return print("Ok")
      """ % (t, UPDATEparams, t)

      methodDELETE = """@api_view(['DELETE'])
def %sRead(request):
    %s = request.query_params.get('%s')
    conn = DbConnection()
    params = [%s]
    result = conn.call_sp('spRead%s', 'one', *params)
    return Response('Deleted ' + %s)""" % (t, firstVar, firstVar, firstVar, t, firstVar)

      SCAN_TESTS = """
def test_%s_scan():
      params = {
            %s
      }
      r = requests.get(APP_URL + '%s-scan/', params=params)
      print(json.loads(r.content))
      if type(json.loads(r.content)) == type(list()):
            return print("Ok")
      """ % (t, SCANparams, t)


      CREATEresult += CREATE_TESTS
      READresult += READ_TESTS
      UPDATEresult += UPDATE_TESTS
      SCANresult += SCAN_TESTS
      result += CREATEresult + READresult + UPDATEresult + SCANresult


text_file = open('DatabasesHelpers/' + DB_NAME + "/Django/tests.txt", "w")
text_file.write(CREATEresult)
text_file.close()

print("Tests created at " + 'DatabasesHelpers/' + DB_NAME + '/Django/')