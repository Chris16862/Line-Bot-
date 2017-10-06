from linebot.models import *
import os
from connection import con
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)
db = con.cursor()

def get_reply(event,status,userid) :
    db.execute("DELETE FROM sell_list WHERE userid='{}' and status='{}'".format(userid, status[0][0]))
    res = db.fetchall()
    print (res)
    con.commit()
    return TextSendMessage(
    	event.reply_token,
    	text="取消成功"
    	)