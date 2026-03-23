from database import DataBase

DB_PATH = "pft.db"

db = DataBase(DB_PATH)

def get_all():
    rows = db.get_categories()
    return [dict(row) for row in rows]


def add(data):
    category = data.get("category")
    result = db.add_new_category(category)
    return {"message": result}

def delete(id):
    result = db.delete_category(id)
    return {"message": result}