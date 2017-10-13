from linebot.models import *
import os
from connection import con
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def get_reply(event, status, userid):
    db = con.cursor()