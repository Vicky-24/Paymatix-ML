from .config_details import SQLSERVER_DB_DRIVER, SQLSERVER_DB_SERVER, SQLSERVER_DB_NAME, SQLSERVER_DB_USER, SQLSERVER_DB_PASSWORD

class DEV:
    SQLSERVER_DB_SERVER = SQLSERVER_DB_SERVER
    SQLSERVER_DB_DRIVER = SQLSERVER_DB_DRIVER
    SQLSERVER_DB_NAME = SQLSERVER_DB_NAME
    SQLSERVER_DB_USER = SQLSERVER_DB_USER
    SQLSERVER_DB_PASSWORD = SQLSERVER_DB_PASSWORD

class UAT:
    DB_USER = ""
    DB_PASSWORD = ""
    DB_HOST = ""
    DB_NAME = ""
    

class PROD:
    DB_USER = ""
    DB_PASSWORD = ""
    DB_HOST = ""
    DB_NAME = ""


def get_env_obj(env=None):

    _configuration = {}
    if env and env == "DEV":
        _configuration["env"] = DEV()
    elif env and env == "UAT":
        _configuration["env"] = UAT()
    else:
        _configuration["env"] = PROD()
        
    return _configuration