from linebot.models import *
from datetime import datetime
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Check(pro_id, con, confirm) :
    if confirm=="yes" :
        db = con.cursor()
        db.execute("UPDATE sell_list SET status='check' WHERE id={}".format(pro_id))
        con.commit()
        db.close()
        return TextSendMessage(text="結單完成")
    elif confirm=="no" :
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="確定結單？",
                actions=[
                PostbackTemplateAction(
                    label='Yes',
                    data='check,{},yes'.format(pro_id),
                    ),
                PostbackTemplateAction(
                    label='No',
                    data='cancel'
                    )
                 ]
            )
         )
