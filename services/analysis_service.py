from utils import paise_to_rupees

# util
def format_data(row):
    return {
            **row,
            "income": paise_to_rupees(row["income"]),
            "expense": paise_to_rupees(row["expense"]),
            "net": paise_to_rupees(row["income"] - row["expense"])
        }
#==========================================================================

def get_total(db, user_id, start_date, end_date):
    income = db.get_total_income(user_id, start_date, end_date)
    expense = db.get_total_expense(user_id, start_date, end_date)
    return{
            "total_income": paise_to_rupees(income),
            "total_expense": paise_to_rupees(expense),
            "net": paise_to_rupees(income-expense)
          }


def get_yearly(db, user_id, start_date, end_date):
    rows = db.get_yearly_report(user_id, start_date, end_date)
    return [format_data(row) for row in rows]
    

def get_monthly(db, user_id, start_date, end_date):
    rows = db.get_monthly_report(user_id, start_date, end_date)
    return [format_data(row) for row in rows]


def get_weekly(db, user_id, start_date, end_date):
    rows = db.get_weekly_report(user_id, start_date, end_date)
    return [format_data(row) for row in rows]


def get_by_categories(db, user_id, start_date, end_date):
    rows = db.get_report_by_categories(user_id, start_date, end_date)
    return [format_data(row) for row in rows]