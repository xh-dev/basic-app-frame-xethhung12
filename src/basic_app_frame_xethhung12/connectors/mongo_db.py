
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# uri = "mongodb+srv://<db_username>:<db_password>@c0.pbqmnnl.mongodb.net/?appName=C0"

class Connector:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def get_mongo_client(url: str, version:int="1"):
        client = MongoClient(uri, server_api=ServerApi(version))
        try:
            client.admin.command('ping')
            return client
        except Exception as e:
            print(e)
    def get_client(self):
        return MongoClient(self.connection_string, server_api=ServerApi("1"))
    

    @staticmethod
    def _credential_with_connection_str(username: str, password: str, connection_str, un_placeholder:str="<db_un>", pwd_placeholder:str="<db_pwd>") -> str:
        safe_username = quote_plus(username)
        safe_password = quote_plus(password)
        return connection_str.replace(un_placeholder, safe_username).replace(db_password, safe_password)
    
    @staticmethod
    def credential_with_connection_str(username: str, password: str, connection_str, un_placeholder:str="<db_un>", pwd_placeholder:str="<db_pwd>") -> str:
        return Connector(Connector._credential_with_connection_str(username, password, connection_str, un_placeholder, pwd_placeholder))
    

    @staticmethod
    def _raw_connection( username: str, password: str, host: str, port: int, database: str):
        safe_username = quote_plus(username)
        safe_password = quote_plus(password)
        return f"mongodb://{safe_username}:{safe_password}@{host}:{port}/{database}"

    @staticmethod
    def raw_connection( username: str, password: str, host: str, port: int, database: str):
        return Connector(Connector._raw_connection(username, password, host, port, database))
