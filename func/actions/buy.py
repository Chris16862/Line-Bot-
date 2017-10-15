from linebot.models import *
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Buy(event, status, userid, con):
    db = con.cursor()
    if not status:
        s="check"
        db.execute("INSERT INTO buy_list (userid, status) VALUES (%s, %s)",(userid, s))
        db.close()
        return TextSendMessage(text="請輸入商品編號:")
    elif status[0][0]=="check":
        buy=event.message.text
        if buy.isdigit():
            s="count"
            db.execute("SELECT name FROM sell_list WHERE id={}".format(int(buy)))
            data=db.fetchall()
            db.execute("UPDATE buy_list SET thing_id={},status='{}' WHERE status='check' and userid='{}'".format(int(buy), s, userid))
            con.commit()
            db.close()
            return TextSendMessage(text="購買商品為: {}\n請輸入購買數量:".format(data[0][0]))
        else :
            db.close()
            return TextSendMessage(text="只需要輸入數字，請重新輸入")
    elif status[0][0]=="count":
        s="modify"
        db.execute("SELECT price,name FROM sell_list WHERE id={}".format(buy))
        data=db.fetchall()
        amount = int(event.message.text)
        total=data[0][0]*amount
        name = data[0][1]
        db.execute("UPDATE buy_list SET status='{}',amount={} WHERE status='count' and userid='{}'".format(s, amount, userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否需要更改\n商品名:"+name+"\n總額:"+str(total)+"購買數量:"+str(amount),
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
    elif status[0][0]=="modify" :
        if event.message.text=='Yes' : 
            db.close()
            return TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='List',
                    text='請問需要更改哪個項目？',
                    actions=[
                        MessageTemplateAction(
                            label='商品',
                            text='商品',
                        ),
                        MessageTemplateAction(
                            label='數量',
                            text='數量'
                        )
                    ]
                )
            )
        elif event.message.text=='No' :
            profile = line_bot_api.get_profile(userid)
            db.execute("SELECT userid,name FROM sell_list WHERE id=(SELECT thing_id FROM buy_list WHERE userid='{}' and status='modify')".format(userid))
            data = db.fetchall()
            seller_id = data[0][0]
            name = data[0][1]
            db.execute("SELECT amount FROM buy_list WHERE userid='{}' and status='modify'".format(userid))
            amount = db.fetchall()
            db.execute("UPDATE buy_list SET status='finish' WHERE status='modify' and userid='{}'".format(userid))
            con.commit()
            line_bot_api.push_message(
                seller_id,
                text="{}購買了您的商品: {}\n 購買數量為: {}".format(profile.display_name, name , str(amount[0][0]))
                )
            db.close()
            return TextSendMessage(text="購買成功")
        elif event.message.text=='商品' :
            db.execute("UPDATE buy_list SET status='check' WHERE status='modify' and userid='{}'".format(userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請重新輸入商品編號:")
        elif event.message.text=='數量' :
            db.execute("UPDATE buy_list SET status='count' WHERE status='modify' and userid='userid'".format(userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請重新輸入購買數量:")