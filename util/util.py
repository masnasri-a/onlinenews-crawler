def month_converter(month:str)->str:
    result = ""
    month = month.lower()
    if month == 'january' or month == 'januari' or month == 'jan':
        result = "01"
    elif month == 'february' or month == 'februari' or month == 'feb':
        result = "02"
    elif month == 'march' or month == 'maret' or month == 'mar':
        result = "03"
    elif month == 'april' or month == 'apr':
        result = "04"
    elif month == 'may' or month == 'mei':
        result = "05"
    elif month == 'june' or month == 'juni' or month == 'jun':
        result = "06"
    elif month == 'july' or month == 'juli' or month == 'jul':
        result = "07"
    elif month == 'august' or month == 'agustus' or month == 'aug':
        result = "08"
    elif month == 'september' or month == 'sept':
        result = "09"
    elif month == 'october' or month == 'oktober' or month == 'oct':
        result = "10"
    elif month == 'november' or month == 'nov':
        result = "11"
    elif month == 'december' or month == 'desember' or month == 'dec':
        result = "12"

    return result