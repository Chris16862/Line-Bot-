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
    elif action=='user_new' :
        db.execute("DELETE FROM user_list WHERE userid='{}' and status='{}'".format(userid, status[0][0]))
    elif action=='user_modify' :
        db.execute("UPDATE user_list SET status='finish' WHERE userid='{}' and status='{}'".format(userid, status[0][0]))
    con.commit()
    db.close()
    return TextSendMessage(
    	text="取消成功"
    	)

def Cancel_Buy(pro_id,userid,con) :
    db = con.cursor()
    db.execute("SELECT status FROM sell_list WHERE id={}".format(pro_id))
    status = db.fetchone()
    if status[0]=="check" :
        db.close()
        return TextSendMessage(text="本商品已出單，無法退貨囉")
    db.execute("SELECT amount FROM buy_list WHERE thing_id={}".format(pro_id))
    amount = db.fetchone()
    db.execute("UPDATE sell_list SET amount=amount+{},status='finish' WHERE id={}".format(amount[0],pro_id))
    con.commit()
    db.execute("DELETE FROM buy_list WHERE thing_id={} and userid='{}'".format(pro_id, userid))
    con.commit()
    db.close()
    return  TextSendMessage(text="取消成功")
