import my_database
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=+9), 'JST')

if __name__ == "__main__":
    yesterday = datetime.now(JST) - timedelta(days=1)
    my_database.set_score("{:%Y%m%d}".format(yesterday),"C1077")