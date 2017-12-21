from linebot.models import *
from datetime import datetime
import os
import csv
from paramiko import SSHClient,AutoAddPolicy
from func.scp import SCPClient
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Excel(thing_id, userid, con) :
    db = con.cursor()
    db.execute("SELECT * FROM buy_list WHERE thing_id={}".format(thing_id))
    data = db.fetchall()
    os.system("touch profile.csv")
    file = open('profile.csv', 'w',encoding='utf-8-sig')
    csvCursor = csv.writer(file)
    csvCursor.writerow(['買家姓名','Line暱稱','電話','購買數量','是否出貨','購買時間'])
    for d in data :
        profile = line_bot_api.get_profile(d[3])
        db.execute("SELECT name,phone FROM user_list WHERE userid='{}'".format(d[3]))
        data_2 = db.fetchone()
        if d[4]=='check' :
            status = 'yes'
        else :
            status = 'no'
        csvCursor.writerow([data_2[0],profile.display_name,data_2[1],d[2],status,d[5]])
        print ([data_2[0],profile.display_name,data_2[1],d[2],status,d[5]])
    file.close()
    server = "cscc.hsexpert.net"
    port = 22
    user = "apie0419"
    password = "a19970419"
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server, port, user, password)
    scp = SCPClient(client.get_transport())
    scp.put('profile.csv','public_html/chatbot-excels/{}.csv'.format(userid))
    scp.close()
    return TextSendMessage(text="stu-web.tkucs.cc/404411240/chatbot-excels/{}.csv".format(userid))
