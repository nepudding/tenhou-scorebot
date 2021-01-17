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

def get_score(room):
    sql = f"SELECT * FROM scores WHERE room_id = '{room}'"
    sql += "ORDER BY date,id"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql)
            ans = list(map(dictcur.fetchall()))
            return ans

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