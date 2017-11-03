from linebot.models import *
from datetime import datetime
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Check(id, con, confirm) :
    db = con.cursor()
    if confirm=="pro_yes" :
        db.execute("UPDATE sell_list SET status='check' WHERE id={}".format(id))
        con.commit()
        db.close()
        return TextSendMessage(text="結單完成")
    elif confirm=="pro_no" :
        db.execute("SELECT status FROM sell_list WHERE id={}".format(id))
        status = db.fetchone()
        if status[0] == "check" :
            db.close()
            return TextSendMessage(text="本商品已結單囉~")
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="確定結單？",
                actions=[
                PostbackTemplateAction(
                    label='Yes',
                    data='check,{},pro_yes'.format(id),
                    ),
                PostbackTemplateAction(
                    label='No',
                    data='cancel'
                    )
                 ]
            )
         )
    elif confirm=="order_yes" :
        db.execute("SELECT userid,thing_id,amount FROM buy_list WHERE id={}".format(id))
        data = db.fetchone()
        db.execute("SELECT userid,name FROM sell_list WHERE id={}".format(data[1]))
        data_2 = db.fetchone()
        db.execute("SELECT name FROM user_list WHERE userid='{}'".format(data_2[0]))
        seller = db.fetchone()
        name = data_2[1]
        amount = data[2]
        push = [
            TextSendMessage(text="賣家姓名: {}\n已將商品出貨，若已收到商品請點下面的按鈕".format(seller[0])),
            TemplateSendMessage(
                alt_text='商品確認',
                template=ButtonsTemplate(
                    thumbnail_image_url='https://stu-web.tkucs.cc/404411240/chatbot-images/pic{}.jpg'.format(data[1]),
                    title='訂單編號#{}'.format(id),
                    text='商品名稱: {}\n購買數量: {}'.format(name, amount),
                    actions=[
                        PostbackTemplateAction(
                            label='已收到商品',
                            data='order_receive,{}'.format(id),
                        )
                    ]
                )
            )
        ]
        line_bot_api.push_message(
            data[0],
            push
        )
        db.execute("UPDATE buy_list SET status='check' WHERE id={}".format(id))
        con.commit()
        db.close()
        return TextSendMessage(text="設定出貨完成")
    elif confirm=="order_get" :
        db.execute("SELECT userid,thing_id FROM buy_list WHERE id={}".format(id))
        data = db.fetchone()
        db.execute("SELECT name FROM user_list WHERE userid='{}'".format(data[0]))
        buyername = db.fetchone()
        db.execute("SELECT userid,name FROM sell_list WHERE id={}".format(data[1]))
        data_2 = db.fetchone()
        line_bot_api.push_message(
            data_2[0],
            TextSendMessage(text="買家已收到了您的商品:{}\n訂單編號#{}已完成".format(data_2[1],id))
        )
        db.execute("DELETE FROM buy_list WHERE id={}".format(id))
        con.commit()
        db.execute("SELECT * FROM buy_list WHERE thing_id={}".format(data[1]))
        if not db.fetchone() :
            line_bot_api.push_message(
                data_2[0],
                TextSendMessage(text="商品編號#{}的買家皆已收到商品，該商品將會自動刪除".format(data[1]))
            )
        return TextSendMessage(text="交易完成")
def Order_Receive(order_id) :
    return TemplateSendMessage(
        alt_text="商品取貨確認",
        template=ConfirmTemplate(
            text="確認收到商品？",
            actions=[
            PostbackTemplateAction(
                label='Yes',
                data='check,{},order_get'.format(order_id)
            ),
            PostbackTemplateAction(
                label='No',
                data='cancel'
                )
            ]
        )
    )