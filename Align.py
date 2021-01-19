import unicodedata
def left(digit, msg, fill=" "):
    for c in msg:
        if unicodedata.east_asian_width(c) in ('F', 'W', 'A'):
            digit -= 2
        else:
            digit -= 1
    return msg + fill * max(0,digit)