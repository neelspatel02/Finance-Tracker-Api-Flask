from database import DataBase

# DB_PATH = "pft.db"

# db = DataBase(DB_PATH)

def get_all(db):
    rows = db.get_categories()
    return [dict(row) for row in rows]


def add(db,data):
    category = data.get("category")
    try:
        db.add_new_category(category)
        return {"message": "Category Added"}, 201
    except ValueError as e:
        return {"message": str(e)}, 400
    
def delete(db, id):
    try:
        db.delete_category(id)
        return {"message": "Category deleted"}, 201
    except ValueError as e:
        return {"message": str(e)}, 400