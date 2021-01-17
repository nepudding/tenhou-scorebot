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

def sql_requests(sql):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            ans = list(cur.fetchall())
            return ans

def current_tournament():
    sql = "SELECT room_id FROM tournaments ORDER BY start_at desc limit 1;"
    ans = sql_requests(sql)
    print("FUGA",ans)
    return ans[0][0]

def get_user():
    sql = "SELECT * FROM nickname;"
    return sql_requests(sql)

def get_score_sum(room):
    sql = f"SELECT B.nickname, sum(A.score) FROM scores A INNER JOIN nickname B ON A.user_name = B.tenhou_name WHERE A.room_id = '{room}' GROUP BY B.nickname ORDER BY sum DESC;"
    return sql_requests(sql)

def set_user(tenhou, nickname):
    sql = f"INSERT INTO nickname (tenhou_name, nickname) VALUES({tenhou}, {nickname});"
    sql_requests(sql)

def update_score(day, room):
    logs = scraping.get_log(day, room)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM scores WHERE date BETWEEN '{day}' AND '{day} 23:59:59' AND room_id = '{room}';")
            sql = "INSERT INTO scores (date, id, user_name, rank, score, room_id) VALUES "
            values = []
            for num in range(len(logs)):
                log = logs[num]
                for i in range(4):
                    name, score = log['score'][i].split(",")
                    values.append(f"('{log['date']}', {num}, '{name}', {i+1}, {score}, '{room}')")
            cur.execute(sql + ",".join(values) + ";")
            return "OK"