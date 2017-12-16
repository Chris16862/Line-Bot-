from linebot.models import *
from datetime import datetime
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Buy(event, status, userid, con):
    db = con.cursor()
    if isinstance(event, PostbackEvent) :
        d = event.postback.data
        data = d.split(",")
        buy = data[1]
        db.execute("SELECT name,status,amount FROM sell_list WHERE id={}".format(int(buy)))
        data = db.fetchall()
        if data[0][1]=="check" :
            db.close()
            return TextSendMessage("本產品已經收單囉～")
        elif data[0][2] <= 0 :
            db.close()
            return TextSendMessage("本商品已售完~")
        db.execute("INSERT INTO buy_list (userid, status, thing_id) VALUES (%s, %s, %s)",(userid, "count", int(buy)))
        con.commit()
        db.close()
        return TextSendMessage(text="購買商品為: {}\n請輸入購買數量:".format(data[0][0]))
    if not status:
        s="enter_num"
        db.execute("INSERT INTO buy_list (userid, status) VALUES (%s, %s)",(userid, s))
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入商品名稱:")
    elif status[0][0]=="enter_num":
        buy=event.message.text
        db.execute("SELECT id,status,amount,price FROM sell_list WHERE id={}".format(buy))
        data=db.fetchall()
        if (id==null) :
            db.close()
            return TextSendMessage(text="商品不存在，請重新輸入商品名稱\n若想取消本次交易，請按\"功能列表\"內的\"取消輸入\"")
        elif data[0][1]=="check" :
            db.close()
            return TextSendMessage("本產品已經收單囉～\n請輸入其他商品編號")
        elif data[0][2]<=0 :
            db.close()
            return TextSendMessage("本商品已售完~ \n請輸入其他商品編號")
        db.execute("DELETE FROM buy_list WHERE userid='{}' and status='enter_num'".format(userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
                    alt_text='template',
                    template=ButtonsTemplate(
                        thumbnail_image_url='https://stu-web.tkucs.cc/404411240/chatbot-images/pic{}.jpg'.format(int(buy)),
                        title='商品編號#{}'.format(int(buy)),
                        text='商品名稱: {}\n單價: {}\n數量: {}'.format(data[0][0], data[0][3], data[0][2]),
                        actions=[
                            PostbackTemplateAction(
                                label='商品詳情',
                                data='info,{}'.format(int(buy)),
                            ),
                            PostbackTemplateAction(
                                label='立即購買',
                                data='buy,{}'.format(int(buy)),
                            ),
                            PostbackTemplateAction(
                                label='觀看原圖',
                                data='picture,{}'.format(int(buy)),
                            )
                        ]
                    )
                )
    elif status[0][0]=="count":
        if event.message.text.isdigit() :
            amount = int(event.message.text)
            s="modify"
            db.execute("SELECT thing_id FROM buy_list WHERE userid='{}' and status='count'".format(userid))
            buy_id = db.fetchall()
            db.execute("SELECT price,name,amount FROM sell_list WHERE id={}".format(buy_id[0][0]))
            data=db.fetchall()
            if amount<=0 :
                return TextSendMessage("請輸入大於0的數字~")
            if data[0][2] < amount :
                db.close()
                return TextSendMessage(text="商品剩餘{}件，請重新輸入購買數量\n若要取消本次交易，請按\"功能列表\"內的\"取消輸入\"".format(data[0][2]))
            total=data[0][0]*amount
            name = data[0][1]
            db.execute("UPDATE buy_list SET status='{}',amount={} WHERE status='count' and userid='{}'".format(s, amount, userid))
            con.commit()
            db.close()
            return TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text="輸入完畢，請確認內容是否正確\n商品名:"+name+"\n總額:"+str(total)+"\n購買數量:"+str(amount),
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes',
                        ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                        )
                    ]
                   )
                )
        else :
            db.close()
            return TextSendMessage(text="只需要輸入數字，請重新輸入\n若要取消本次交易，請按\"功能列表\"內的\"取消輸入\"")
    elif status[0][0]=="modify" :
        if event.message.text=='Yes' : 
            dt = datetime.now()
            input_dt = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day) + " " + str((dt.hour+8)%24) + ":" + str(dt.minute) + ":" + str(dt.second)
            profile = line_bot_api.get_profile(userid)
            db.execute("SELECT userid,name,id FROM sell_list WHERE id=(SELECT thing_id FROM buy_list WHERE userid='{}' and status='modify')".format(userid))
            data = db.fetchall()
            seller_id = data[0][0]
            name = data[0][1]
            thing_id = data[0][2]
            db.execute("SELECT amount FROM buy_list WHERE userid='{}' and status='modify'".format(userid))
            amount = db.fetchall()[0][0]
            db.execute("UPDATE sell_list SET amount=amount-{} WHERE id ={}".format(amount, thing_id))
            db.execute("UPDATE buy_list SET input_time = TIMESTAMP '{}',status='finish' WHERE status='modify' and userid='{}'".format(input_dt, userid))
            con.commit()
            line_bot_api.push_message(
                seller_id,
                TextSendMessage(
                    text="{}購買了您的商品: {}\n 購買數量為: {}".format(profile.display_name, name , str(amount))
                )
            )
            db.close()
            return TextSendMessage(text="購買成功")
        elif event.message.text=='No' :
            line_bot_api.push_message(
                userid,
                TextSendMessage(
                    text="請點選需要更改的項目"
                )
            )
            db.close()
            return ImagemapSendMessage(
                base_url='https://stu-web.tkucs.cc/404411091/linebot/Change/130.png?_ignored=',
                alt_text='this is an imagemap',
                base_size=BaseSize(height=130, width=1040),
                actions=[
                    MessageImagemapAction(
                        text='商品',
                        area=ImagemapArea(
                            x=0, y=0, width=346, height=130
                        )
                    ),
                    MessageImagemapAction(
                        text='數量',
                        area=ImagemapArea(
                            x=347, y=0, width=346, height=130
                        )
                    ),
                    MessageImagemapAction(
                        text='Yes',
                        area=ImagemapArea(
                            x=694, y=0, width=346, height=130
                        )
                    )
                ]
            )
        elif event.message.text=='商品' :
            db.execute("UPDATE buy_list SET status='check' WHERE status='modify' and userid='{}'".format(userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請重新輸入商品編號:")
        elif event.message.text=='數量' :
            db.execute("UPDATE buy_list SET status='count' WHERE status='modify' and userid='{}'".format(userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請重新輸入購買數量:")
        else :
            db.execute("SELECT name,price FROM sell_list WHERE id=(SELECT thing_id FROM buy_list WHERE userid='{}' and status='modify')".format(userid))
            data = db.fetchone()
            name = data[0]
            price = data[1]
            db.execute("SELECT amount FROM buy_list WHERE status='modify' and userid='{}'".format(userid))
            data = db.fetchone()
            amount = data[0]
            total = price * amount
            db.close()
            return TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text="輸入完畢，請確認內容是否正確\n商品名:"+name+"\n總額:"+str(total)+"\n購買數量:"+str(amount),
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes',
                        ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                        )
                    ]
                   )
                )
