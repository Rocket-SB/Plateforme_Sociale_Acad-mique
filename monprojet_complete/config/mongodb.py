import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from django.conf import settings
try:
    import certifi
except ImportError:
    certifi = None

class MongoDB:
    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            mongo_settings = settings.MONGODB_SETTINGS
            connection_string = f"mongodb://{mongo_settings['host']}:{mongo_settings['port']}/"
            
            if mongo_settings.get('username') and mongo_settings.get('password'):
                connection_string = f"mongodb://{mongo_settings['username']}:{mongo_settings['password']}@{mongo_settings['host']}:{mongo_settings['port']}/"
            
            cls._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                retryWrites=True,
                ssl_ca_certs=certifi.where() if os.getenv('USE_SSL') else None
            )
            try:
                # The ismaster command is cheap and does not require auth.
                cls._client.admin.command('ismaster')
            except ConnectionFailure:
                print("MongoDB server not available")
                cls._client = None
        return cls._client

    @classmethod
    def get_database(cls):
        if cls._db is None:
            client = cls.get_client()
            if client:
                cls._db = client[settings.MONGODB_SETTINGS['database']]
        return cls._db

    @classmethod
    def get_collection(cls, name):
        db = cls.get_database()
        if db:
            return db[name]
        return None

    @classmethod
    def close_connection(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None

def get_db():
    return MongoDB.get_database()

def get_collection(name):
    return MongoDB.get_collection(name)

# Collections
publications_coll = lambda: get_collection('publications')
users_coll = lambda: get_collection('users')
groups_coll = lambda: get_collection('groups')
