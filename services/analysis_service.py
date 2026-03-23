from utils import paise_to_rupees

def get_total(db, user_id):
    income = db.get_total_income(user_id)
    expense = db.get_total_expense(user_id)
    return{
            "total_income": paise_to_rupees(income),
            "total_expense": paise_to_rupees(expense),
            "net": paise_to_rupees(income-expense)
          }


def get_monthly(db, user_id):
    rows = db.get_monthly_report(user_id)
    return [dict(row) for row in rows]


def get_by_categories(db, user_id):
    rows = db.get_report_by_categories(user_id)
    return [dict(row) for row in rows]