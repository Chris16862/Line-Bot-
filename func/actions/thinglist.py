from linebot.models import *
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def ThingList(userid, count, con) :
    if count == -1 :
        return TextSendMessage(text="沒有上一頁了！")
    elif count == -2 :
        return TextSendMessage(text="沒有下一頁了！")
    db = con.cursor()
    db.execute("SELECT * FROM buy_list WHERE userid='{}' and thing_id<{} ORDER BY id DESC LIMIT 5 ".format(userid, count))
    data = db.fetchall()
    buy = []
    for d in data :
        db.execute("SELECT price,userid,name,userid FROM sell_list WHERE id={}".format(d[1]))
        d2 = db.fetchall()
        buy.append(
            CarouselColumn(
                title='商品編號#{}\n'.format(d[1]),
                text='商品名稱: {}\n總價: {}\n數量: {}'.format(d2[2],d1[0]*d[3],d[3]),
                actions=[
                    MessageTemplateAction(
                        label='詳細資料',
                        text="TEST"
                    ),
                    PostbackTemplateAction(
                        label='立即購買',
                        data="TEST"
                    )
                ]
            )
        )
    db.execute("SELECT thing_id FROM buy_list WHERE userid='{}' and thing_id>{} ORDER BY id ASC LIMIT 6".format(userid, count))
    data2 = db.fetchall()
    db.execute("SELECT thing_id FROM buy_list WHERE userid='{}' ORDER BY id ASC LIMIT 1".format(userid))
    max = db.fetchone()
    if not data2 :
        lpg = -1
    else : 
        lpg = data2[len(data2)-1][0]
        if lpg == max[0][0] :
            lpg += 1
    print ("lpg = %s",(lpg,))
    db.execute("SELECT thing_id FROM buy_list WHERE userid='{}' and thing_id<{}".format(userid, data[len(data)-1][1]))
    if db.fetchone() :
        npg = data[len(data)-1][1]
    else :
        npg = -2
    print ("ngp = %s",(npg,))
    line_bot_api.push_message(
        userid,
        TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=buy,
            )
        )
    )
    db.close()
    return TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text="選單",
            actions=[
                PostbackTemplateAction(
                    label='上一頁',
                    data='thinglist_turnpg,{}'.format(lpg)
                ),
                PostbackTemplateAction(
                    label='下一頁',
                    data='thinglist_turnpg,{}'.format(npg)
                )
            ]
        )
    )