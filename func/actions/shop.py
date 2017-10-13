from linebot.models import *
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Shop(userid,con) :
    db = con.cursor()
    db.execute("SELECT * FROM sell_list")
    data = db.fetchall()
    thing = []
    for d in data :
        thing.append(
            CarouselColumn(
                title='商品編號#{}'.format(d[0]),
                text='商品名稱: {}\n單價: {}\n剩餘數量: {}'.format(d[2],d[3],d[4]),
                actions=[
                    MessageTemplateAction(
                        label='詳細資料',
                        text=d[5]
                    )
                ]
            )
        )
    return TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=thing
            )
        )