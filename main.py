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

import my_database

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

def aggregate_score():
    sql = my_database.get_score("C1077")
    return sql



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    hoge = event.message.text
    if hoge.startswith("にゃーん"):
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage("にゃ〜ん"),TextSendMessage("にゃ〜ん"),
            TextSendMessage("にゃにゃにゃ"),TextSendMessage("にゃにゃにゃ")]
        )
    if hoge.startswith("きろく"):
        data = aggregate_score()
        texts = []
        for i in data:
            texts.append(TextSendMessage(str(i)))
        line_bot_api.reply_message(
            event.reply_token,
            texts
        )
    if hoge.startswith("こうしん"):
        _, date, room = hoge.split()
        res = my_database.update_score(date, room)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res)
        )


if __name__ == "__main__":
    print("にゃーん")
    port = int(os.getenv("PORT","80"))
    app.run(host="0.0.0.0", port=port)