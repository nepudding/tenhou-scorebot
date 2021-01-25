import os
from datetime import datetime, timedelta, timezone
import re
import psycopg2
from psycopg2.extras import DictCursor

import scraping

DATABASE_URL = os.environ.get('DATABASE_URL')

JST = timezone(timedelta(hours=+9), 'JST')

def get_connection():
    dsn = os.environ.get('DATABASE_URL')
    return psycopg2.connect(dsn)

def sql_requests(sql, res=True):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            if res:
                ans = list(cur.fetchall())
                return ans

def current_tournament():
    sql = "SELECT room_id, url, name FROM tournaments ORDER BY start_at desc limit 1;"
    ans = sql_requests(sql)
    return ans[0][0], ans[0][1], ans[0][2]

def set_tournament(name,room,url):
    time = "{:%Y%m%d %H:%M:%S}".format(datetime.now(JST))
    sql = f"UPDATE tournaments SET name='{name}', start_at = '{time}', url = '{url}' WHERE room_id='{room}';" \
          f"INSERT INTO tournaments (name,  room_id, start_at, url) SELECT '{name}', '{room}', '{time}', '{url}'" \
          f"WHERE NOT EXISTS (SELECT room_id FROM tournaments WHERE room_id='{room}')"
    sql_requests(sql,res=False)
    return f"大会名：{name}を登録しました"

def get_score_sum(room):
    sql = f"SELECT B.nickname, sum(A.score) FROM scores A INNER JOIN nickname B ON A.user_name = B.tenhou_name WHERE A.room_id = '{room}' GROUP BY B.nickname ORDER BY sum DESC;"
    return sql_requests(sql)

def set_user(nickname, tenhou):
    sql = f"UPDATE nickname SET nickname='{nickname}' WHERE tenhou_name='{tenhou}';" \
          f"INSERT INTO nickname (nickname, tenhou_name) SELECT '{nickname}', '{tenhou}'" \
          f"WHERE NOT EXISTS (SELECT tenhou_name FROM nickname WHERE tenhou_name='{tenhou}')"
    sql_requests(sql, res=False)

def init_user():
    sql = f"INSERT INTO nickname(nickname, tenhou_name)"\
           "SELECT DISTINCT user_name, user_name FROM scores "\
           "WHERE NOT EXISTS (SELECT tenhou_name FROM nickname WHERE tenhou_name=user_name); "
    sql_requests(sql, res=False)

def update_score(day, room):
    init_user()
    logs = scraping.get_log(day, room)
    if len(logs) == 0:
        return f"{day}に対戦がありません"
    values = []
    for num in range(len(logs)):
        log = logs[num]
        for i in range(4):
            name, score = log['score'][i].split(",")
            values.append(f"('{log['date']}', {num}, '{name}', {i+1}, {score}, '{room}')")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM scores WHERE date BETWEEN '{day}' AND '{day} 23:59:59' AND room_id = '{room}';")
            sql = "INSERT INTO scores (date, id, user_name, rank, score, room_id) VALUES "
            cur.execute(sql + ",".join(values) + ";")
            return "OK"

def get_log(day):
    init_user()
    sql = f"SELECT * FROM scores WHERE date BETWEEN '20210116' AND '20210116 23:59:59' ORDER BY date, id, rank;"
    
    """
    SELECT s.date,s.id,s.score,s.rank, n.nickname, t.name FROM scores s
    INNER JOIN nickname n ON s.user_name = n.tenhou_name
    INNER JOIN tournaments t ON s.room_id = t.room_id
    WHERE s.date BETWEEN '20210120' AND '20210121'   
    ORDER BY s.date, s.id, s.rank;
    """
    a =  sql_requests(sql)
    out = []
    for i in range(0, len(a), 4):
        for j in range(i,i+4):
            hoge = {}
