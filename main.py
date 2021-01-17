from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os
import re

import psycopg2
from psycopg2.extras import DictCursor

import scraping

from datetime import datetime, timedelta, timezone

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN', None)
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET', None)
DATABASE_URL = os.environ.get('DATABASE_URL')

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

JST = timezone(timedelta(hours=+9), 'JST')

def get_connection():
    dsn = os.environ.get('DATABASE_URL')
    return psycopg2.connect(dsn)

def get_score(room):
    sql = f"SELECT * FROM scores ORDER BY date WHERE room_id = '{room}'"
    sql += "ORDER BY date"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql)
            out = cur.fetchall()
            return out

def set_score(day, room):
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

@app.route('/')
def hello_world():
    return 'hello world'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    hoge = event.message.text
    if hoge.startswith("にゃーん"):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="にゃ〜ん")
        )
    if hoge.startswith("こうしん"):
        _, room = hoge.split()
        date = "{:%Y%m%d}".format(datetime.now(JST))
        res = set_score(date, room)
        TextSendMessage(text=res)


if __name__ == "__main__":
    print("にゃーん")
    port = int(os.getenv("PORT","80"))
    app.run(host="0.0.0.0", port=port)