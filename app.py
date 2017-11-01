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
        elif isinstance(event.source, SourceGroup) :
            print (event)
            if isinstance(event, PostbackEvent) :
                d = event.postback.data
                data = d.split(",")
                if data[0] == "info" :
                    line_bot_api.reply_message(
                        event.reply_token,
                        Product(
                            data[1],
                            con
                            )
                        )
            continue
        userid = event.source.user_id
        db.execute("SELECT status FROM sell_list WHERE status!='finish' and userid='{}'".format(userid))
        sell_status = db.fetchall()
        db.execute("SELECT status FROM user_list WHERE status!='finish' and userid='{}'".format(userid))
        user_status = db.fetchall()
        db.execute("SELECT status FROM buy_list WHERE status!='finish' and userid='{}'".format(userid))
        buy_status = db.fetchall()
        if isinstance(event, PostbackEvent) :
            if sell_status or user_status or buy_status :
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="您還未完成之前的交易，請先輸入完畢\n若想取消本次交易，請按\"功能列表\"內的\"取消輸入\""
                    )
                )
                continue
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
            elif data[0]=="shop_turnpg" :
                line_bot_api.reply_message(
                    event.reply_token,
                    Shop(
                        userid,
                        int(data[1]),
                        con
                        )
                    )
            elif data[0]=="thinglist_turnpg" :
                line_bot_api.reply_message(
                    event.reply_token,
                    ThingList(
                        userid,
                        int(data[1]),
                        con
                        )
                    )
            elif data[0]=="contact" :
                profile = line_bot_api.get_profile(data[1])
                db.execute("SELECT name,phone FROM user_list WHERE userid='{}'".format(data[1]))
                p = db.fetchone()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="姓名: {}\nLine暱稱: {}\n聯絡電話: {}".format(p[0],profile.display_name, p[1])
                    )
                )
            elif data[0]=="buyer" :
                db.execute("SELECT userid,amount,id,input_time FROM buy_list WHERE thing_id={} ORDER BY id ASC".format(data[1]))
                data = db.fetchall()
                if not data :
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="尚無買家")
                    )
                    return "OK"
                reply = []
                for d in data :
                    profile = line_bot_api.get_profile(d[0])
                    db.execute("SELECT name,phone FROM user_list WHERE userid='{}'".format(d[0]))
                    buyer_data = db.fetchone()
                    r = "訂單編號#{}\n買家: {} 真實姓名: {}\n聯絡方式:{}\n購買數量: {}\n時間: {}\n".format(d[2],profile.display_name, buyer_data[0], buyer_data[1],d[1],str(d[3]))
                    if len("\n\n".join(reply)) + len(r) >= 1000 :
                        line_bot_api.push_message(
                            userid,
                            TextSendMessage(
                                text="\n".join(reply)
                            )
                        )
                        reply = []
                    reply.append(r)
                line_bot_api.push_message(
                    userid,
                    TextSendMessage(
                       text="\n".join(reply) 
                    )
                )
            elif data[0]=="info" :
                line_bot_api.reply_message(
                        event.reply_token,
                        Product(
                            data[1],
                            con
                        )
                    )
            elif data[0]=="check" :
                line_bot_api.reply_message(
                    event.reply_token,
                    Check(
                        data[1],
                        con,
                        data[2]
                    )
                )
            elif data[0]=="cancel" :
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="OK"
                        )
                )
        if isinstance(event.message, ImageMessage) and sell_status:
            line_bot_api.reply_message(
                event.reply_token,
                Sell(
                    event,
                    sell_status,
                    userid,
                    con
                    )
            )
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        db.execute("SELECT * FROM user_list WHERE userid='{}'".format(userid))
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
        elif (event.message.text=="/Sell" or sell_status) and not buy_status and not user_status :
            line_bot_api.reply_message(
                event.reply_token,
                Sell(
                    event,
                    sell_status,
                    userid,
                    con
                    )
                )
        elif event.message.text=="/Buy" or buy_status and not sell_status and not user_status :
            line_bot_api.reply_message(
                event.reply_token,
                Buy(
                    event,
                    buy_status,
                    userid,
                    con
                    )
                )
        elif event.message.text=='/BuyList' and not buy_status and not user_status and not sell_status:
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
                            ),
                            MessageTemplateAction(
                                label='我的購買清單',
                                text='/ThingList',
                            )
                        ]
                    )
                )
            )
        elif event.message.text=='/SellList' and not buy_status and not user_status and not sell_status :
             line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='功能選單',
                        text='請選擇想使用的功能',
                        actions=[
                            MessageTemplateAction(
                                label='我的商品',
                                text='/BuyerList',
                            ),
                            MessageTemplateAction(
                                label='查看訂單',
                                text='Test',
                            )
                        ]
                    )
                )
            )
        elif (event.message.text=="/Info" or user_status) and not buy_status and not sell_status :
            line_bot_api.reply_message(
                event.reply_token,
                Info(
                    event,
                    userid,
                    user_status,
                    con
                    )
                )
        elif event.message.text=="/Shop" and not buy_status and not user_status and not sell_status :
            db.execute("SELECT id FROM sell_list WHERE status='finish' and amount>0 ORDER BY id DESC LIMIT 1")
            count = db.fetchall()
            line_bot_api.reply_message(
                event.reply_token,
                Shop(
                    userid,
                    count[0][0]+1,
                    con
                    )
                )
        elif event.message.text=="/ThingList" and not buy_status and not user_status and not sell_status :
            db.execute("SELECT id FROM buy_list WHERE userid='{}' ORDER BY id DESC LIMIT 1".format(userid))
            count = db.fetchall()
            line_bot_api.reply_message(
                event.reply_token,
                ThingList(
                    userid,
                    count[0][0]+1,
                    con
                )
            )
        elif event.message.text=="/BuyerList" and not buy_status and not user_status and not sell_status :
            db.execute("SELECT id FROM sell_list WHERE userid='{}' ORDER BY id DESC LIMIT 1".format(userid))
            count = db.fetchone()
            line_bot_api.reply_message(
                event.reply_token,
                BuyerList(
                    userid,
                    count[0]+1,
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
