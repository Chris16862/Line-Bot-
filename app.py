# -*- encoding: utf8 -*-
import os
import sys
from argparse import ArgumentParser
from func.connection import con
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from func.actions import *

app = Flask(__name__)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
db = con.cursor()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    for event in events:
        userid = event.source.user_id
        if isinstance(event, JoinEvent) :
            db.execute("INSERT INTO group_list (grid) VALUES (%s)", (event.source.group_id,))
            con.commit()
            continue
        elif isinstance(event, LeaveEvent):
            db.execute("DELETE FROM group_list WHERE grid='{}'".format(event.source.group_id))
            con.commit()
            continue
        elif isinstance(event, FollowEvent) :
            db.execute("INSERT INTO user_list(userid,status) VALUES (%s,%s)", (event.source.user_id,"new",))
            con.commit()
            continue
        if isinstance(event, PostbackEvent) :
            d = event.postback.data
            data = d.split(",")
            if data[0]=="buy" :
                line_bot_api.reply_message(
                    event.reply_token,
                    Buy(
                        event,
                        [],
                        userid,
                        con
                        )
                )
            if data[0]=="shop_turnpg" :
                line_bot_api.reply_message(
                    event.reply_token,
                    Shop(
                        userid,
                        int(data[1]),
                        con
                        )
                    )
            if data[0]=="thinglist_turnpg" :
                line_bot_api.reply_message(
                    event.reply_token,
                    ThingList(
                        userid,
                        int(data[1]),
                        con
                        )
                    )
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.source, SourceUser) :
            print (event.message.text)
            continue
        if isinstance(event.message, ImageMessage) :
            line_bot_api.reply_message(
                event.reply_token,
                #p.get_reply(event)
                ImageSendMessage(
                    original_content_url="https://www.google.com.tw/url?sa=i&rct=j&q=&esrc=s&source=images&cd=&cad=rja&uact=8&ved=0ahUKEwjZz_Db9czWAhVDn5QKHcpiCuoQjRwIBw&url=http%3A%2F%2Fhotlink.go2tutor.com%2Fcontent.asp%3Fid%3D7630&psig=AOvVaw380rFvoti8qdnNZIu8nYJe&ust=1506860903874606",
                    preview_image_url="https://stickershop.line-scdn.net/stickershop/v1/product/1254734/LINEStorePC/main@2x.png;compress=true"
                    )
                )
        db.execute("SELECT userid FROM user_list WHERE userid='{}'".format(userid))
        if not db.fetchall() :
            db.execute("INSERT INTO user_list(userid,status) VALUES (%s,%s)", (event.source.user_id,"new",))
            con.commit()
        db.execute("SELECT * FROM user_list WHERE userid='{}' and status='new'".format(userid))
        if db.fetchall() and event.message.text!="/Info" :
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(
                    text="需填寫用戶資料，才能使用功能，請點選功能列表內的用戶資料"
                    )
                )
            return "OK"
        db.execute("SELECT status FROM sell_list WHERE status!='finish' and userid='{}'".format(userid))
        sell_status = db.fetchall()
        db.execute("SELECT status FROM user_list WHERE status!='finish' and userid='{}'".format(userid))
        user_status = db.fetchall()
        db.execute("SELECT status FROM buy_list WHERE status!='finish' and userid='{}'".format(userid))
        buy_status = db.fetchall()
        print (user_status)
        if event.message.text=="/Cancel" and (sell_status or buy_status) :
            if sell_status :
                line_bot_api.reply_message(
                    event.reply_token,
                        Cancel(
                            sell_status,
                            "sell",
                            userid,
                            con
                            )
                    )
            elif buy_status :
                line_bot_api.reply_message(
                    event.reply_token,
                        Cancel(
                            buy_status,
                            "buy",
                            userid,
                            con
                            )
                    )
        elif event.message.text=="/Sell" or sell_status :
            line_bot_api.reply_message(
                event.reply_token,
                Sell(
                    event,
                    sell_status,
                    userid,
                    con
                    )
                )
        elif event.message.text=="/Buy" or buy_status :
            line_bot_api.reply_message(
                event.reply_token,
                Buy(
                    event,
                    buy_status,
                    userid,
                    con
                    )
                )
        elif event.message.text=='/BuyList' :
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='功能選單',
                        text='請選擇想使用的功能',
                        actions=[
                            MessageTemplateAction(
                                label='商品清單',
                                text='/Shop',
                            )
                        ]
                    )
                )
            )
        elif event.message.text=='/SellList' :
             line_bot_api.reply_message(
                event.reply_token,
                TextMessage(
                    text="不好意思,此功能尚未開放,敬請期待"
                    )
                )
        elif event.message.text=="/Info" or user_status :
            line_bot_api.reply_message(
                event.reply_token,
                Info(
                    event,
                    userid,
                    user_status,
                    con
                    )
                )
        elif event.message.text=="/Shop" :
            db.execute("SELECT id FROM sell_list ORDER BY id DESC LIMIT 1")
            count = db.fetchall()
            line_bot_api.reply_message(
                event.reply_token,
                Shop(
                    userid,
                    count[0][0]+1,
                    con
                    )
                )
    return 'OK'
   


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    app.run(debug=options.debug, port=options.port)
