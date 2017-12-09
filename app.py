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
        db.execute("SELECT * FROM user_list WHERE userid='{}'".format(userid))
        if not db.fetchall() :
            db.execute("INSERT INTO user_list(userid,status) VALUES (%s,%s)", (userid,"new",))
            con.commit()
        db.execute("SELECT status FROM sell_list WHERE status!='finish' and status!='check' and userid='{}'".format(userid))
        sell_status = db.fetchall()
        db.execute("SELECT status FROM user_list WHERE status!='finish' and userid='{}'".format(userid))
        user_status = db.fetchall()
        db.execute("SELECT status FROM buy_list WHERE status!='finish' and status!='check' and userid='{}'".format(userid))
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
            elif data[0]=="buyerlist_turnpg" :
                line_bot_api.reply_message(
                    event.reply_token,
                    BuyerList(
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
                line_bot_api.reply_message(
                    event.reply_token,
                    ShowBuyer(
                        data[1], 
                        userid, 
                        con
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
            elif data[0]=="order_receive" :
                line_bot_api.reply_message(
                    event.reply_token,
                    Order_Receive(
                        data[1],
                    )
                )
            elif data[0]=="cancel" :
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="OK"
                        )
                )
            elif data[0]=="cancel_buy" :
                line_bot_api.reply_message(
                    event.reply_token,
                    Cancel_Buy(
                        data[1],
                        userid,
                        con
                    )
                )
            elif data[0]=="export" :
                line_bot_api.push_message(
                    userid,
                    TextSendMessage("建立表格中，請稍候...")
                )
                line_bot_api.reply_message(
                    event.reply_token,
                    Excel(
                        data[1],
                        userid,
                        con
                    )
                )
            elif data[0]=="picture" :
                line_bot_api.reply_message(
                    event.reply_token,
                    Trans_Pic(
                        data[1]
                    )
                )
        if not isinstance(event, MessageEvent):
            continue
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
        if not isinstance(event.message, TextMessage):
            continue
        db.execute("SELECT * FROM user_list WHERE userid='{}' and status='new'".format(userid))
        if db.fetchall() and event.message.text!="用戶資料" :
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(
                    text="需填寫用戶資料，才能使用功能，請點選\"功能列表\"內的\"用戶資料\""
                    )
                )
            return "OK"
        if event.message.text=="取消" :
            if sell_status :
                c_status = sell_status
                action = 'sell'
            elif buy_status :
                c_status = buy_status
                action = 'buy'
            elif user_status:
                if user_status[0][0]=='modify_name' or user_status[0][0]=='modify_phone' or user_status[0][0]=='modify' or user_status[0][0]=="searching":
                    c_status = user_status
                    action = 'user_modify'
                else :
                    c_status = user_status
                    action = 'user_new'
            else :
                line_bot_api.reply_message(
                    event.reply_token,
                    TextMessage(text="目前沒有輸入東西喔～")
                )
                continue
            line_bot_api.reply_message(
                    event.reply_token,
                        Cancel(
                            c_status,
                            action,
                            userid,
                            con
                        )
                )
        elif sell_status :
            line_bot_api.reply_message(
                event.reply_token,
                Sell(
                    event,
                    sell_status,
                    userid,
                    con
                )
            )
        elif buy_status :
            line_bot_api.reply_message(
                event.reply_token,
                Buy(
                    event,
                    buy_status,
                    userid,
                    con
                )
            )
        elif user_status :
            if user_status[0][0] == "searching" :
                line_bot_api.reply_message(
                    event.reply_token,
                    Search(
                    event.message.text,
                    userid,
                    con
                    )
                )
            else :
                line_bot_api.reply_message(
                event.reply_token,
                Info(
                    event,
                    userid,
                    user_status,
                    con
                )
            )
        elif event.message.text=="賣東西" :
            line_bot_api.reply_message(
                event.reply_token,
                Sell(
                    event,
                    sell_status,
                    userid,
                    con
                )
            )
        elif event.message.text=="搜尋商品" :
            line_bot_api.reply_message(
                event.reply_token,
                Buy(
                    event,
                    buy_status,
                    userid,
                    con
                )
            )
        elif event.message.text=='買家專區' :
            line_bot_api.reply_message(
                event.reply_token,
                ImagemapSendMessage(
                    base_url='https://stu-web.tkucs.cc/404411091/linebot/ButtonBuy/1040.png?_ignored=',
                    alt_text='買家專區',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        MessageImagemapAction(
                            text='商城',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=520
                            )
                        ),
                        MessageImagemapAction(
                            text='我的購買清單',
                            area=ImagemapArea(
                                x=0, y=520, width=520, height=520
                            )
                        ),
                        MessageImagemapAction(
                            text='搜尋商品',
                            area=ImagemapArea(
                                x=520, y=520, width=520, height=520
                            )
                        )
                    ]
                )
            )
        elif event.message.text=='賣家專區' :
             line_bot_api.reply_message(
                event.reply_token,
                ImagemapSendMessage(
                    base_url='https://stu-web.tkucs.cc/404411091/linebot/ButtonSell/1040.png?_ignored=',
                    alt_text='賣家專區',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        MessageImagemapAction(
                            text='賣東西',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=520
                            )
                        ),
                        MessageImagemapAction(
                            text='出貨',
                            area=ImagemapArea(
                                x=0, y=520, width=520, height=520
                            )
                        ),
                        MessageImagemapAction(
                            text='商品管理',
                            area=ImagemapArea(
                                x=520, y=520, width=520, height=520
                            )
                        )
                    ]
                )
            )
        elif event.message.text=="用戶資料" :
            line_bot_api.reply_message(
                event.reply_token,
                Info(
                    event,
                    userid,
                    user_status,
                    con
                    )
                )
        elif event.message.text=="商城" :
            db.execute("SELECT id FROM sell_list WHERE status='finish' and amount>0 ORDER BY id DESC LIMIT 1")
            count = db.fetchall()
            if not count :
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="目前系統中無販賣中的商品喔～"
                    )
                )
            else :
                line_bot_api.reply_message(
                    event.reply_token,
                    Shop(
                        userid,
                        count[0][0]+1,
                        con
                        )
                    )
        elif event.message.text=="我的購買清單" :
            db.execute("SELECT id FROM buy_list WHERE userid='{}' ORDER BY id DESC LIMIT 1".format(userid))
            count = db.fetchall()
            if not count :
                reply = TextSendMessage(text="您目前已無購買的商品囉~")
            else :
                reply = ThingList(
                    userid,
                    count[0][0]+1,
                    con
                )
            line_bot_api.reply_message(
                event.reply_token,
                reply
            )
        elif event.message.text=="商品管理" :
            db.execute("SELECT id FROM sell_list WHERE userid='{}' ORDER BY id DESC LIMIT 1".format(userid))
            count = db.fetchone()
            if not count :
                reply = TextSendMessage(text="您目前已無販賣中的商品囉~")
            else :
                reply = BuyerList(
                    userid,
                    count[0]+1,
                    con
                )
            line_bot_api.reply_message(
                event.reply_token,
                reply
            )
        elif event.message.text=="出貨" :
            db.execute("UPDATE user_list SET status='searching' WHERE userid='{}'".format(userid))
            con.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入訂單編號: ")
                )
        else :
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="點選下方功能列表內的按鈕，即可使用功能喔～～")
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
