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
    db.execute("SELECT id FROM sell_list WHERE userid='{}' ORDER BY id DESC LIMIT 1".format(userid))
    max = db.fetchall()
    db.execute("SELECT * FROM sell_list WHERE id<{} and userid='{}' ORDER BY id DESC LIMIT 5".format(count,userid))
    data = db.fetchall()
    print (data)
    thing = []
    for d in data :
        if d[6] == 'check' :
            addition = '(已收單)'
        else :
            addition = ''
        thing.append(
            CarouselColumn(
                thumbnail_image_url='https://stu-web.tkucs.cc/404411240/chatbot-images/pic{}.jpg'.format(d[0]),
                title='商品編號#{}\n{}'.format(d[0],addition),
                text='商品名稱: {}\n單價: {}\n剩餘數量: {}'.format(d[2],d[3],d[4]),
                actions=[
                    PostbackTemplateAction(
                        label='查看買家',
                        data='buyer,{}'.format(d[0])
                    ),
                    PostbackTemplateAction(
                        label='收單',
                        data='check,{},pro_no'.format(d[0])
                    )
                ]
            )
        )
    db.execute("SELECT id FROM sell_list WHERE id>{} and userid='{}' ORDER BY id ASC LIMIT 6".format(data[0][0],userid))
    c = db.fetchall()
    if count == max[0][0]+1 :
        lpg = 0
    else :
        lpg = c[len(c)-1][0]
        if lpg == max[0][0] :
            lpg += 1
    db.execute("SELECT id FROM sell_list WHERE id<{} and userid='{}'".format(data[len(data)-1][0],userid))
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
        alt_text='我的商品',
        template=ConfirmTemplate(
            text="我的商品",
            actions=[
                PostbackTemplateAction(
                    label='上一頁',
                    data='buyerlist_turnpg,{}'.format(lpg)
                ),
                PostbackTemplateAction(
                    label='下一頁',
                    data='buyerlist_turnpg,{}'.format(npg)
                )
            ]
        )
    )
def ShowBuyer(thing_id, userid, con) :
    db = con.cursor()
    db.execute("SELECT userid,amount,id,input_time,status FROM buy_list WHERE thing_id={} ORDER BY id ASC".format(thing_id))
    data = db.fetchall()
    if not data :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="尚無買家")
        )
        return "OK"
    reply = []
    for d in data :
        profile = line_bot_api.get_profile(d[0])
        b_status = ''
        if d[4] == "check" :
            b_status = '(已出貨)' 
        db.execute("SELECT name,phone FROM user_list WHERE userid='{}'".format(d[0]))
        buyer_data = db.fetchone()
        r = "訂單編號#{} {}\n買家: {} 真實姓名: {}\n聯絡方式:{}\n購買數量: {}\n時間: {}\n".format(d[2],b_status,profile.display_name, buyer_data[0], buyer_data[1],d[1],str(d[3]))
        if len("\n\n".join(reply)) + len(r) >= 1000 :
            line_bot_api.push_message(
                userid,
                TextSendMessage(
                    text="\n".join(reply)
                )
            )
            reply = []
        reply.append(r)
    line_bot_api.push_message(
        userid,
        TextSendMessage(
           text="\n".join(reply) 
        )
    )
    db.close()
    return TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text="是否需要將用戶資料匯出成表格?",
            actions=[
                PostbackTemplateAction(
                    label='Yes',
                    data='export,{}'.format(thing_id)
                ),
                PostbackTemplateAction(
                    label='No',
                    data='cancel'
                )
            ]
        )
    )