from linebot.models import *
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Cancel(status,action,userid,con) :
    db = con.cursor()
    if action=="sell" :
        db.execute("DELETE FROM sell_list WHERE userid='{}' and status='{}'".format(userid, status[0][0]))
    elif action=="buy" :
        db.execute("DELETE FROM buy_list WHERE userid='{}' and status='{}'".format(userid, status[0][0]))
    con.commit()
    db.close()
    return TextSendMessage(
    	text="取消成功"
    	)