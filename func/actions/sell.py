from linebot.models import *
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Sell(event, status, userid,con) :
    db = con.cursor()
    if not status :
        s = "enter_name"
        db.execute("INSERT INTO sell_list (userid, status) VALUES (%s, %s)",(userid, s))
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入商品名:")
    elif status[0][0]=="enter_name":
        s = "enter_price"
        SQL = "UPDATE sell_list SET name='{}',status='{}' WHERE status='enter_name' and userid='{}';".format(event.message.text, s, userid)
        db.execute(SQL)
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入單價:")
    elif status[0][0]=="enter_price":
        s = "enter_amount"
        db.execute("UPDATE sell_list SET price={},status='{}' WHERE status='enter_price' and userid='{}'".format(int(event.message.text), s, userid))
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入提供數量:")
    elif status[0][0]=="enter_amount":
        s = "enter_intro"
        db.execute("UPDATE sell_list SET amount={},status='{}' WHERE status='enter_amount' and userid='{}'".format(int(event.message.text), s, userid))
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入介紹或優惠:")
    elif status[0][0]=="enter_intro":
        s = "modify"
        db.execute("SELECT name,price,amount FROM sell_list WHERE status='enter_intro' and userid='{}'".format(userid))
        data = db.fetchall()
        db.execute("UPDATE sell_list SET intro='{}',status='{}' WHERE status='enter_intro' and userid='{}'".format(event.message.text, s, userid))
        con.commit()
        db.close()
        line_bot_api.push_message(
            userid,
            TextSendMessage(
                text="商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+str(data[0][2])+"\n介紹及優惠:"+event.message.text
                )
            )
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否需要更改",
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
    elif status[0][0]=="modify_name":
        db.execute("SELECT price,amount,intro FROM sell_list WHERE status='modify_name' and userid='{}'".format(userid))
        data = db.fetchall()
        s = "modify"
        SQL = "UPDATE sell_list SET name='{}',status='{}' WHERE status='modify_name' and userid='{}';".format(event.message.text, s, userid)
        db.execute(SQL)
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否需要更改\n商品名:"+event.message.text+"\n單價:"+str(data[0][0])+"\n數量:"+str(data[0][1])+"\n介紹及優惠:"+data[0][2],
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
    elif status[0][0]=="modify_price":
        db.execute("SELECT name,amount,intro FROM sell_list WHERE status='modify_price' and userid='{}'".format(userid))
        data = db.fetchall()
        s = "modify"
        db.execute("UPDATE sell_list SET price={},status='{}' WHERE status='modify_price' and userid='{}'".format(int(event.message.text), s, userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否需要更改\n商品名:"+data[0][0]+"\n單價:"+event.message.text+"\n數量:"+str(data[0][1])+"\n介紹及優惠:"+data[0][2],
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
    elif status[0][0]=="modify_amount":
        db.execute("SELECT name,price,intro FROM sell_list WHERE status='modify_amount' and userid='{}'".format(userid))
        data = db.fetchall()
        s = "modify"
        db.execute("UPDATE sell_list SET amount={},status='{}' WHERE status='modify_amount' and userid='{}'".format(int(event.message.text), s, userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+event.message.text+"\n介紹及優惠:"+data[0][2],
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
    elif status[0][0]=="modify_intro":
        db.execute("SELECT name,price,amount FROM sell_list WHERE status='modify_intro' and userid='{}'".format(userid))
        data = db.fetchall()
        s = "modify"
        db.execute("UPDATE sell_list SET intro='{}',status='{}' WHERE status='modify_intro' and userid='{}'".format(event.message.text, s, userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否需要更改\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+str(data[0][2])+"\n介紹及優惠:"+event.message.text,
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
            s = 'finish'
            db.execute("SELECT * FROM group_list")
            ids = db.fetchall()
            db.execute("SELECT intro,id,name,amount,price FROM sell_list WHERE userid='{}' and status='modify'".format(userid))
            data = db.fetchall()
            intro = data[0][0]
            number = data[0][1]
            name = data[0][2]
            amount = data[0][3]
            price = data[0][4]
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            profile = line_bot_api.get_profile(userid)
            for i in ids :
                line_bot_api.push_message(
                i[0],
                TextSendMessage(text="商品編號#"+str(number)+"\n賣家: "+profile.display_name+"\n商品名:"+name+"\n單價:"+str(price)+"\n數量:"+str(amount)+"\n\n"+intro+"\n如需購買請私訊我喔～")
                )
            return TextSendMessage(text="產品新增成功")
        elif event.message.text=='No' :
            return TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='List',
                        text='請問需要更改哪個項目？',
                        actions=[
                        MessageTemplateAction(
                            label='商品名',
                            text='商品名',
                            ),
                        MessageTemplateAction(
                            label='單價',
                            text='單價'
                            ),
                        MessageTemplateAction(
                            label='數量',
                            text='數量'
                            ),
                        MessageTemplateAction(
                            label='介紹及優惠',
                            text='介紹及優惠'
                            )
                        ]
                        )
                    )
        elif event.message.text=="商品名" :
            s = "modify_name"
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            return  TextSendMessage(text="請輸入商品名:")
        elif event.message.text=="單價" :
            s = "modify_price"
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請輸入單價:")
        elif event.message.text=="數量" :
            s = "modify_amount"
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請輸入數量:")
        elif event.message.text=="介紹及優惠":
            s = "modify_intro"
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請輸入介紹及優惠:")