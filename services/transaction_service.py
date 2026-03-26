import math
from utils import rupees_to_paise, convert_to_datetime_str, paise_to_rupees

SORT_OPTIONS = {"date": "t.t_date",
               "amount" : "t.amount_in_paise",
               "type" : "t.t_type",
               "category": "c.category",
               "entry_date" : "t.created_at"
               }


def format_transaction(row):
    return {
        "id": row["t_id"],
        "date": row["date"],
        "time": row["time"],
        "amount": paise_to_rupees(row["amount_in_paise"]),
        "type": row["t_type"],
        "category": row["category"],
        "description": row["description"]
    }


def get_paginated(db, page, limit, sort_by, sort_order, user_id, filters):
    offset = (page - 1) * limit
    sort_col = SORT_OPTIONS.get(sort_by, "t.t_date")
    total = db.get_transactions_count(user_id)
    total_pages = math.ceil(total / limit)
    filters = filters or {}

    rows = db.get_transactions(user_id, filters, sort_col, sort_order, limit, offset)

    return {"transactions": [format_transaction(row) for row in rows],
            "page": page,
            "total_pages": total_pages}


# def get_all(db, user_id):
#     rows = db.get_transactions(user_id)
#     return [format_transaction(row) for row in rows]


def add(db, data, user_id):
    db_data = {
        "user_id": user_id,
        "t_datetime": convert_to_datetime_str(data["date"], data.get("time", "00:00:00")),
        "amount_in_paise": rupees_to_paise(data["amount"]),
        "t_type": data["t_type"],
        "category_id": int(data["category_id"]),
        "description": data.get("description", "").strip() 
    }

    try:
        db.add_transaction(db_data)
        return {"message": "Transaction added"}, 201
    except ValueError as e:
        return {"message": str(e)}, 400
    

def delete(db, transaction_id):
    try:
        db.delete_transaction(transaction_id)
        return {"message": "Transactions Deleted"}, 201
    except ValueError as e:
        return {"message": str(e)}, 400