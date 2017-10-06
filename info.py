from linebot.models import *
import os
import re
from connection import con
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)
db = con.cursor()

def get_reply(event, userid, status) :
    if status[0][0] == "new" :
        db.execute("UPDATE user_list SET status='enter_name' WHERE userid='{}'".format(userid))
        con.commit()
        return TextSendMessage(
    	text="您是第一次輸入資料\n請先輸入姓名:"
    	)
    elif status[0][0] == "enter_name" :
        db.execute("UPDATE user_list SET status='enter_phone', name='{}' WHERE userid='{}'".format(event.message.text, userid))
        con.commit()
        return TextSendMessage(
    	text="請輸入手機號碼 : "
    	)
    elif status[0][0] == "enter_phone" :
        if len(event.message.text)!=10 or not re.match(r'09(.+)',event.message.text) :
            return TextSendMessage(
    	    text="格式輸入錯誤 請重新輸入"
    	)
        db.execute("UPDATE user_list SET status='modify', phone='{}' WHERE userid='{}'".format(event.message.text, userid))
        con.commit()
        db.execute("SELECT name FROM user_list WHERE userid='{}'".format(userid))
        data = db.fetchall()
        return TemplateSendMessage(
	        alt_text='Confirm template',
	        template=ConfirmTemplate(
	            text="輸入完畢，請確認內容是否需要更改\n姓名:"+data[0][0]+"\n手機:"+event.message.text,
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
    elif status[0][0] == "modify" :
        if event.message.text == "Yes" :
            return TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='用戶資料',
                    text='請問需要哪個項目？',
                    actions=[
                    MessageTemplateAction(
                        label='姓名',
                        text='姓名',
                        ),
                    MessageTemplateAction(
                        label='手機',
                        text='手機'
                        ),
                     ]
                )
            )
        elif event.message.text == "No" :
        	db.execute("UPDATE user_list SET status='finish' WHERE userid='{}'".format(userid))
        	con.commit()
        	return TextSendMessage(
        		text="用戶資料更改完成"
        		)
        elif event.message.text == "姓名" :
        	db.execute("UPDATE user_list SET status='modify_name' WHERE userid='{}'".format(userid))
        	con.commit()
        	return TextSendMessage(
        		text="請先輸入姓名:"
        		)
        elif event.message.text == "手機" :
        	db.execute("UPDATE user_list SET status='modify_phone' WHERE userid='{}'".format(userid))
        	con.commit()
        	return TextSendMessage(
        		text="請輸入手機號碼 : "
        		)
    elif status[0][0] == "modify_name" :
        db.execute("UPDATE user_list SET status='modify' WHERE userid='{}'".format(userid))
        con.commit()
        db.execute("SELECT phone FROM user_list WHERE userid='{}'".format(userid))
        data = db.fetchall()
        return TemplateSendMessage(
	        alt_text='Confirm template',
	        template=ConfirmTemplate(
	            text="輸入完畢，請確認內容是否需要更改\n姓名:"+event.message.text+"\n手機:"+data[0][0],
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
    elif status[0][0] == "modify_phone" :
        db.execute("UPDATE user_list SET status='modify' WHERE userid='{}'".format(userid))
        con.commit()
        db.execute("SELECT name FROM user_list WHERE userid='{}'".format(userid))
        data = db.fetchall()
        return TemplateSendMessage(
	        alt_text='Confirm template',
	        template=ConfirmTemplate(
	            text="輸入完畢，請確認內容是否需要更改\n姓名:"+data[0][0]+"\n手機:"+event.message.text,
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