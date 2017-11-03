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
        db.execute("UPDATE buy_list SET status='check' WHERE id=(%s,)",(id,))
        con.commit()
        db.close()
        return TextSendMessage(text="設定出貨完成")
