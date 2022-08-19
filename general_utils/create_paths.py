from db_handler.mysql_dbconn import DbConnection 
import os

conn = DbConnection()
paths = [
  'DatabasesHelpers/%s/' % (conn.db_name),
  'DatabasesHelpers/%s/SP/CREATE/' % (conn.db_name),
  'DatabasesHelpers/%s/SP/READ/' % (conn.db_name),
  'DatabasesHelpers/%s/SP/UPDATE/' % (conn.db_name),
  'DatabasesHelpers/%s/SP/DELETE/' % (conn.db_name),
  'DatabasesHelpers/%s/SP/SOFT_DELETE/' % (conn.db_name),
  'DatabasesHelpers/%s/SP/SCAN/' % (conn.db_name),
  'DatabasesHelpers/%s/SQL_QUERYS/' % (conn.db_name),
  'DatabasesHelpers/%s/Django/' % (conn.db_name),
]

for path in paths:
  # Check whether the specified path exists or not
  path_exists = os.path.exists(path)

  if not path_exists:
    
    # Create a new directory because it does not exist 
    os.makedirs(path)
print("Created Directories!")
