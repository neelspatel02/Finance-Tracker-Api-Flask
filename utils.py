from decimal import Decimal

def rupees_to_paise(amount):
    return int(Decimal(str(amount))*100)

def paise_to_rupees(paise):
    return str(Decimal(paise)/Decimal(100))

def convert_to_datetime_str(date_str, time_str="00:00:00"):
    if len(time_str) == 5:
        time_str += ":00"
    
    return f"{date_str} {time_str}"