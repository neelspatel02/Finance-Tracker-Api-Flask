from utils import rupees_to_paise, convert_to_datetime_str

def format_transaction(row):
    return {
        "id": row["t_id"],
        "date": row["date"],
        "time": row["time"],
        "amount": rupees_to_paise(row["amount_in_paise"]),
        "type": row["t_type"],
        "category": row["category"],
        "description": row["description"]
    }


def get_all(db, user_id):
    rows = db.get_transactions(user_id)
    return [format_transaction(row) for row in rows]


def add(db, data, user_id):
    db_data = {
        "user_id": user_id,
        "t_datetime": convert_to_datetime_str(data["date"], data.get("time", "00:00:00")),
        "amount_in_paise": rupees_to_paise(data["amount"]),
        "t_type": data["t_type"],
        "category_id": int(data["category_id"]),
        "description": data.get("description", "").strip() 
    }

    db.add_transaction(db_data)
    return {"message": "Transaction added"}


def delete(db, id):
    db.delete_transaction(id)
    return {"message": "Transactions Deleted"}