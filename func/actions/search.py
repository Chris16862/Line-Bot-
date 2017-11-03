from linebot.models import *
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Search(order_id,userid,con) :
    if not order_id.isdigit() :
        return TextSendMessage("訂單編號必須為數字喔～\n若想取消本次交易，請按\"功能列表\"內的\"取消輸入\"")
    db = con.cursor()
    db.execute("SELECT userid,thing_id,amount FROM buy_list WHERE id = {}".format(order_id))
    data = db.fetchone()
    if not data :
        return TextSendMessage("訂單不存在")
    db.execute("SELECT userid,name FROM sell_list WHERE id = {}".format(data[1]))
    data_2 = db.fetchone()
    if userid!=data_2[0] :
        db.close()
        return TextSendMessage(text="這不是您的訂單喔~\n請重新輸入")
    db.execute("SELECT name FROM user_list WHERE userid = '{}'".format(data[0]))
    buyer_name = db.fetchone()
    name = data_2[1]
    amount = data[2]
    db.execute("UPDATE user_list SET status='finish' WHERE userid='{}'".format(userid))
    con.commit()
    db.close()
    return TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text="輸入完畢\n商品名:"+name+"\n購買數量:"+str(amount)+"\n買家姓名: "+buyer_name[0]+"\n確認出貨？",
            actions=[
            PostbackTemplateAction(
                label='Yes',
                data='check,{},order_yes'.format(order_id),
                ),
            PostbackTemplateAction(
                label='No',
                data='cancel'
                )
            ]
           )
        )