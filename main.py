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

import my_database, Align

from datetime import datetime, timedelta, timezone

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN', None)
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET', None)

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

JST = timezone(timedelta(hours=+9), 'JST')

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
            TextSendMessage("にゃ〜ん")
        )
    if hoge.startswith("せいせき"):
        ct = my_database.current_tournament()
        score = my_database.get_score_sum(ct)
        text = f"{ct}"
        for r in score:
            text += "\n"
            text += Align.left(16,r[0]) + "：" + str(r[1]) 
        print(text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text)
        )
    if hoge.startswith("こうしん"):
        _, date, room = hoge.split()
        sql = f"SELECT room_id FROM tournaments WHERE name='{room}'"
        room = my_database.sql_requests(sql)[0][0]
        res = my_database.update_score(date, room)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res)
        )
    
    if hoge.startswith("ゆーざー"):
        _, nickname, id = hoge.split()
        my_database.set_user(nickname, id)





if __name__ == "__main__":
    print("にゃーん")
    port = int(os.getenv("PORT","80"))
    app.run(host="0.0.0.0", port=port)