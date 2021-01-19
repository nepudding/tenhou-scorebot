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
    sql = "SELECT room_id, url FROM tournaments ORDER BY start_at desc limit 1;"
    ans = sql_requests(sql)
    return ans[0]['room_id'], ans[0]['url']

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
           "WHERE NOT EXISTS (SELECT tenhou_name FROM nickname WHERE tenhou_name=nickname); "
    sql_requests(sql, res=False)

def update_score(day, room):
    init_user()
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