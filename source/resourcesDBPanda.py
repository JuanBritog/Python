import os
from sqlalchemy import create_engine

def create_connection(config_path_db):
    if not os.path.exists(config_path_db):
        raise FileNotFoundError(f"Il file {config_path_db} non esiste.")
    
    properties = read_properties(config_path_db)
    
    UID = properties['dbUser']
    PWD = properties['dbPwd']
    dbUrl = properties['dbUrl']

    # Estrai DATABASE e SERVER da dbUrl
    database_index = dbUrl.find('DatabaseName=') + len('DatabaseName=')
    DATABASE = dbUrl[database_index:]

    server_start_index = dbUrl.find('//') + len('//')
    server_end_index = dbUrl.find(':', server_start_index)
    SERVER = dbUrl[server_start_index:server_end_index]
    connection_string = (
               f"mssql+pyodbc://{UID}:{PWD}@{SERVER}/{DATABASE}?"
              f"driver=SQL Server"
              
           )

   
   # Crea la connessione al database
    engine = create_engine(connection_string)
    connection = engine.connect()
    return connection
   

def read_properties(file_path):
    properties = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                properties[key.strip()] = value.strip()
    return properties