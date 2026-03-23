from datetime import datetime

def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%m-%d").strftime("%m-%d")
    except ValueError:
        return None