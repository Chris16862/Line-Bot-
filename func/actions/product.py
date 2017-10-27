from linebot.models import *
from datetime import datetime
import os
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Product(p_id, con) :
    db = con.cursor()
    db.execute("SELECT userid,intro FROM sell_list WHERE id = {}".format(p_id))
    data = db.fetchone()
    db.execute("SELECT name,phone FROM user_list WHERE userid='{}'".format(data[0]))
    seller_data = db.fetchone()
    profile = line_bot_api.get_profile(data[0])
    db.close()
    return TextSendMessage(
        text="賣家姓名: {}\nLine暱稱: {}\n聯絡方式: {}\n商品介紹及優惠:\n{}".format(seller_data[0],profile.display_name,seller_data[1],data[1]))