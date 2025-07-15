# import pyodbc #pymysql #removed pymysql dependecy from the project

from sqlalchemy.engine import URL
from sqlalchemy import create_engine

from .env import access

class Query:
    def __init__(self, type, username, password, db_name, host_or_server, port_or_driver):
        
        allowedDbTypes = ['sqlserver', 'sql']
        if not type in allowedDbTypes :
            raise "Invalid DB Type: Please provide either 'sqlserver' or 'sql' as type"
        
        self.type = type
        self.db_name = db_name
        self.password = password
        self.username = username
        self.host_or_server = host_or_server
        self.port_or_driver = port_or_driver

    # def connection(self):
    #     if self.type == 'sql':
    #         sqlEngine = pymysql.connect(host=self.host_or_server,
    #                          user=self.username,
    #                          password=self.password,
    #                          database=self.db_name,
    #                          cursorclass=pymysql.cursors.DictCursor)
    #         return sqlEngine
    #     elif self.type == 'sqlserver':
    #         engine = pyodbc.connect(driver='{ODBC Driver 18 for SQL Server}', host='arguspoc.database.windows.net', database='arguspocdb1',
    #                 user='ArgusPOCAdmin@arguspoc', password='AzureArgus@100')
    #         return engine
    #     else:    
    #         raise "Invalid DB Type: Please provide either 'sqlserver' or 'sql' as type"

    
    def alchemy_connect(self):
        if self.type == 'sqlserver':
            conn_string = (
                f"DRIVER={self.port_or_driver};SERVER={self.host_or_server};DATABASE={self.db_name};UID={self.username};PWD={self.password}"
            )
            conn_url = URL.create("mssql+pyodbc", query={"odbc_connect": conn_string})
            engine = create_engine(conn_url)
            
            return engine
        elif self.type == 'sql':
            sqlEngine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                .format(host=self.host_or_server, db=self.db_name, user=self.username, pw=self.password))
            
            return sqlEngine
        else:    
            raise "Invalid DB Type: Please provide either 'sqlserver' or 'sql' as type"


    def execute(self, sql):
        with self.connection().cursor() as cursor:
            cursor.execute(sql)
            # fetchone -> to read single data
            result = cursor.fetchall()
            return result

sqlServerObj = Query('sqlserver', access.SQLSERVER_DB_USER, access.SQLSERVER_DB_PASSWORD, access.SQLSERVER_DB_NAME, access.SQLSERVER_DB_SERVER, access.SQLSERVER_DB_DRIVER)
# sqlObj = Query('sql', access.DB_USER, access.DB_PASSWORD, access.DB_NAME, access.DB_HOST, access.DB_PORT)

# print(sqlServerObj.alchemy_connect())
# print(sqlObj.alchemy_connect().connect())
# print(sqlServerObj.execute("SELECT \
#  * \
#  FROM \
#  CustomerTable;"))