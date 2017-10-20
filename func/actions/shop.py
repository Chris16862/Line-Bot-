from linebot.models import *
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Shop(userid,count,con) :
    db = con.cursor()
    db.execute("SELECT id FROM sell_list ORDER BY id DESC LIMIT 1")
    max = db.fetchall()
    if count == -1 :
        return TextSendMessage(text="沒有下一頁了！")
    elif count == 0 :
        return TextSendMessage(text="沒有上一頁了！")
    db.execute("SELECT * FROM sell_list WHERE id<{} ORDER BY id DESC LIMIT 5 ".format(count))
    data = db.fetchall()
    print (data)
    thing = []
    for d in data :
        thing.append(
            CarouselColumn(
                title='商品編號#{}'.format(d[0]),
                text='商品名稱: {}\n賣家: {}\n單價: {}\n剩餘數量: {}'.format(d[2],d[1],d[3],d[4]),
                actions=[
                    MessageTemplateAction(
                        label='詳細資料',
                        text=d[5]
                    ),
                    PostbackTemplateAction(
                        label='立即購買',
                        data='buy,{}'.format(d[0])
                    )
                ]
            )
        )
    line_bot_api.push_message(
        userid,
        TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=thing
            )
        )
    )
    db.execute("SELECT id FROM sell_list WHERE id>{} LIMIT 6".format(data[0][0]))
    c = db.fetchall()
    print (c)
    if count == max[0][0]+1 :
        npg = 0
    else :
        npg = c[len(c)-1][0]
        if npg == max[0][0] :
            npg += 1
    db.execute("SELECT id FROM sell_list WHERE id<{}".format(data[len(data)-1][0]))
    if db.fetchone() :
        lpg = data[len(data)-1][0]
    else :
        lpg = -1
    print (lpg)
    return TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text="選單",
            actions=[
                PostbackTemplateAction(
                    label='上一頁',
                    data='turnpg,{}'.format(npg)
                ),
                PostbackTemplateAction(
                    label='下一頁',
                    data='turnpg,{}'.format(lpg)
                )
            ]
        )
    )