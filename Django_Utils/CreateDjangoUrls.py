from db_handler.mysql_dbconn import DbConnection 

conn = DbConnection()
for t in conn.get_table_names():
    url_create = 'path("%s-create/", views.%sCreate, name="%s-create"),' % (t,t,t)
    url_read = 'path("%s-read/", views.%sRead, name="%s-read"),' % (t,t,t)
    url_update = 'path("%s-update/", views.%sUpdate, name="%s-update"),' % (t,t,t)
    url_delete = 'path("%s-delete/", views.%sDelete, name="%s-delete"),' % (t,t,t)
    url_scan = 'path("%s-scan/", views.%sScan, name="%s-scan"),' % (t,t,t)

    print(url_create)
    print(url_read)
    print(url_update)
    print(url_delete)
    print(url_scan)
    print("")
    