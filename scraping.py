import urllib.request
import urllib.error
import gzip
import codecs
from datetime import datetime, timedelta, timezone

_URL = "https://tenhou.net/sc/raw/dat/sca{}.log.gz"
JST = timezone(timedelta(hours=+9), 'JST')

def get_today(format='%Y%m%d'):
    return datetime.now(JST).strftime(format)

def download_log(day):
    url = _URL.format(day)
    try :
        gz_path = f"/tmp/{day}.log.gz"
        urllib.request.urlretrieve(url,gz_path)
        with gzip.open(gz_path,"rb") as f:
            newname = f"/tmp/{day}.log"
            reader = codecs.getreader("utf-8")
            contents = reader(f)
            with open(newname, "w", encoding="utf-8") as newf:
                newf.write(contents.read())
    except urllib.error as e:
        print(e)

if __name__ == "__main__":
    day = get_today()
    download_log(day)
    with open(f"/tmp/{day}.log") as log:
        for line in log:
            if "C9506" in line:
                print(line)