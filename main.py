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

import my_database, parsing

from datetime import datetime, timedelta, timezone, time

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
    command = parsing.parsing(hoge)
    if command == None:
        return
    elif command['command'] == 'にゃーん':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("にゃ〜ん")
        )
    elif command['command'] == 'せいせき':
        room_id, _, room_name = my_database.current_tournament()

        today = datetime.now(JST)
        my_database.update_score("{:%Y%m%d}".format(today), room_id)
        if today.time() < time(1,0,0):
            my_database.update_score("{:%Y%m%d}".format(today-timedelta(days=1)), room_id)

        score = my_database.get_score_sum(room_id)
        text = f"{room_name}"
        for r in score:
            text += "\n"
            text += r[0] + "：" + str(r[1]) 
        print(text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text)
        )
    elif command['command'] == "こうしん":
        if len(command['args']) != 2:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="usage : -こうしん [date(YYYYmmdd)] [大会名]"))
            return
        
        date, taikai = command['args']
        sql = f"SELECT room_id FROM tournaments WHERE name='{taikai}'"
        room = my_database.sql_requests(sql)[0][0]
        res = my_database.update_score(date, room)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res)
        )
#    elif command["command"] == "たいかいとうろく":
#        if len(command['args']) != 3:
#            line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text="usage : -たいかいとうろく [name] [roomid] [url]"))
#            return
#        name, room, url = command['args']
#        text = my_database.set_tournament(name, room, url)
#        line_bot_api.reply_message(
#            event.reply_token,
#            TextSendMessage(text=text))

    elif command['command'] == "ゆーざー":
        if len(command['args']) != 2:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="usage : -ゆーざー [name] [tenhouId]"))
            return
        nickname, tenhou_id = command['args']
        my_database.set_user(nickname, tenhou_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{tenhou_id}を{nickname}さんのアカウントとして記憶しました。"))

    elif command['command'] == 'ろぐ':
        day = 
        if len(command['args'] == 0):
            day = "{:%Y%m%d}".format(datetime.now(JST).date())
        elif len(command['args'] == 1):
            try:
                tdatetime = "{:%Y%m%d}".format(datetime.strptime(command['args'][0],"%Y%m%d"))
                days.append()
            except ValueError:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="引数は YYYYmmdd の形で入力して下さい"))
                return
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="usage : -ろぐ [day(YYYYmmdd)]"))
        text = "\n".join(my_database.get_log(day))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))

if __name__ == "__main__":
    print("にゃーん")
    port = int(os.getenv("PORT","80"))
    app.run(host="0.0.0.0", port=port)