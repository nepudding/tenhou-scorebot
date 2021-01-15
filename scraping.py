import urllib.request
import urllib.error
import gzip
import codecs
from datetime import datetime, timedelta, timezone
import re, random, string

_URL = "https://tenhou.net/sc/raw/dat/sca{}.log.gz"
_OLD_URL = "https://tenhou.net/sc/raw/dat/{}/sca{}.log.gz"
JST = timezone(timedelta(hours=+9), 'JST')

def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

def get_log(day, ROOM):
    name = randomname(4)
    print(name)
    url = _URL.format(day)
    if download_file(url, name):
        url = _OLD_URL.format(day[:4],day)
        print(url)
        if download_file(url, name):
            return -1
    with open(f"/tmp/{name}.log","rb") as f:
        reader = codecs.getreader("utf-8")
        contents = reader(f)
        out = []
        for line in contents.readlines():
            if not re.match(rf"{ROOM}*",line):
                continue
            _, time, _, score = re.split(r"\ \|\ ",line[:-2])
            hoge = {}
            hoge["date"] = day+"".join(time.split(":"))
            scores = {}
            for i in score.split():
                name, point = i[:-1].split("(")
                scores[name] = float(point)
            hoge["score"] = scores
            out.append(hoge)
        return out
    return "OK"

def download_file(url, name):
    try :
        gz_path = f"/tmp/{name}.log.gz"
        urllib.request.urlretrieve(url,gz_path)
        with gzip.open(f"/tmp/{name}.log.gz","rb") as f:
            with open(f"/tmp/{name}.log", "w") as nf:
                reader = codecs.getreader("utf-8")
                contents = reader(f)
                nf.write(contents.read())
        return 0
    except:
        return -1

if __name__ == "__main__":
    day = input()
    print(get_log(day,"C1077"))