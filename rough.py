from database import DataBase

DB_PATH = "pft.db"


db = DataBase(DB_PATH)
db.connect()
db.create_tables()


data = db.delete_category(6)
print(data)

row = db