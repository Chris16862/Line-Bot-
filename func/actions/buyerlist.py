from linebot.models import *
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def BuyerList(userid, count, con) :
    #db.execute("SELECT * FROM buy_list WHERE id<{} and thing_id IN (SELECT id FROM sell_list WHERE userid='{}') ORDER BY id DESC LIMIT 5".format(count,userid))
    #data = db.fetchall()
    if count == -1 :
        return TextSendMessage(text="沒有下一頁了！")
    elif count == 0 :
        return TextSendMessage(text="沒有上一頁了！")
    db = con.cursor()
    db.execute("SELECT id FROM sell_list WHERE status = 'finish' and userid='{}' ORDER BY id DESC LIMIT 1".format(userid))
    max = db.fetchall()
    db.execute("SELECT * FROM sell_list WHERE id<{} and status = 'finish' and userid='{}' ORDER BY id DESC LIMIT 5".format(count,userid))
    data = db.fetchall()
    print (data)
    thing = []
    for d in data :
        thing.append(
            CarouselColumn(
                title='商品編號#{}\n'.format(d[0]),
                text='商品名稱: {}\n單價: {}\n剩餘數量: {}'.format(d[2],d[3],d[4]),
                actions=[
                    PostbackTemplateAction(
                        label='查看買家',
                        data='buyer,{}'.format(d[0])
                    ),
                    PostbackTemplateAction(
                        label='出單',
                        data='Test'
                    )
                ]
            )
        )
    db.execute("SELECT id FROM sell_list WHERE id>{} and status = 'finish' ORDER BY id ASC LIMIT 6".format(data[0][0]))
    c = db.fetchall()
    if count == max[0][0]+1 :
        lpg = 0
    else :
        lpg = c[len(c)-1][0]
        if lpg == max[0][0] :
            lpg += 1
    db.execute("SELECT id FROM sell_list WHERE id<{} and status='finish'".format(data[len(data)-1][0]))
    if db.fetchone() :
        npg = data[len(data)-1][0]
    else :
        npg = -1
    print ("lpg = ",lpg)
    print ("npg = ",npg)
    line_bot_api.push_message(
        userid,
        TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=thing,
            )
        )
    )
    return TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text="選單",
            actions=[
                PostbackTemplateAction(
                    label='上一頁',
                    data='shop_turnpg,{}'.format(lpg)
                ),
                PostbackTemplateAction(
                    label='下一頁',
                    data='shop_turnpg,{}'.format(npg)
                )
            ]
        )
    )