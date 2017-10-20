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
    db.execute("SELECT * FROM buy_list WHERE userid='{}' and id<{} and status='finish' ORDER BY id DESC LIMIT 5 ".format(userid, count))
    data = db.fetchall()
    buy = []
    for d in data :
        db.execute("SELECT price,name,userid FROM sell_list WHERE id={}".format(d[1]))
        d2 = db.fetchall()
        print (d)
        print (d2)
        buy.append(
            CarouselColumn(
                title='訂單編號#{}\n'.format(d[0]),
                text='商品名稱: {}\n總價: {}\n數量: {}'.format(d2[0][1],d2[0][0]*d[2],d[2]),
                actions=[
                    PostbackTemplateAction(
                        label='聯絡賣家',
                        data="contact,{}".format(d2[0][2])
                    ),
                    MessageTemplateAction(
                        label='取消購買',
                        text="TEST"
                    )
                ]
            )
        )
    db.execute("SELECT id FROM buy_list WHERE userid='{}' and id>{} and status ='finish' ORDER BY id ASC LIMIT 6".format(userid, count))
    data2 = db.fetchall()
    db.execute("SELECT id FROM buy_list WHERE userid='{}' and status = 'finish' ORDER BY id DESC LIMIT 1".format(userid))
    max = db.fetchone()
    print ("max = ",max)
    print ("data2 = ",data2)
    if not data2 :
        lpg = -1
    else : 
        lpg = data2[len(data2)-1][0]
        if lpg == max[0] :
            lpg += 1
    db.execute("SELECT id FROM buy_list WHERE userid='{}' and status='finish' and id<{}".format(userid, data[len(data)-1][1]))
    if db.fetchone() :
        npg = data[len(data)-1][1]
    else :
        npg = -2
    print ("lpg = ",lpg)
    print ("npg = ",npg)
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