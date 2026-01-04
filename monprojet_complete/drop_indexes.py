from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['research_platform_mongo']
for coll in ['publications', 'users', 'groups']:
    db[coll].drop_indexes()
    print(f"✅ Cleared indexes for {coll}")