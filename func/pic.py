from paramiko import SSHClient,AutoAddPolicy
from scp import SCPClient
from PIL import Image
from linebot.models import *
import os
from linebot import LineBotApi

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def save_pic(event,pic_id) :
        os.system("touch pic.jpg")
        os.system("touch pic-p.jpg")
        os.system("touch pic-o.jpg")
        message_content = line_bot_api.get_message_content(event.message.id)
        with open('pic.jpg', 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        img = Image.open('pic.jpg')
        new_img= img.resize((240, 160),Image.ANTIALIAS)
        new_img.save('pic-p.jpg',quality=100)
        new_img = img.resize((1024, 720),Image.ANTIALIAS)
        new_img.save('pic-o.jpg',quality=100)
        server = "cscc.hsexpert.net"
        port = 22
        user = "apie0419"
        password = "a19970419"
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(server, port, user, password)
        scp = SCPClient(client.get_transport())
        scp.put('pic-o.jpg','public_html/chatbot-images/pic{}.jpg'.format(pic_id))
        scp.put('pic-p.jpg','public_html/chatbot-images/pic-p{}.jpg'.format(pic_id))
        scp.close()
        return "OK"
        