from paramiko import SSHClient,AutoAddPolicy
from scp import SCPClient
from PIL import Image
from linebot.models import *
import os
from linebot import LineBotApi

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def get_reply(event) :
        os.system("touch pic.jpeg")
        os.system("touch pic-p.jpeg")
        os.system("touch pic-o.jpeg")
        message_content = line_bot_api.get_message_content(event.message.id)
        with open('pic.jpeg', 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        img = Image.open('pic.jpeg')
        new_img= img.resize((240, 160),Image.ANTIALIAS)
        new_img.save('pic-p.jpeg',quality=100)
        new_img = img.resize((1024, 720),Image.ANTIALIAS)
        new_img.save('pic-o.jpeg',quality=100)
        server = "cscc.hsexpert.net"
        port = 22
        user = "apie0419"
        password = "a19970419"
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(server, port, user, password)
        scp = SCPClient(client.get_transport())
        scp.put('pic-o.jpeg','public_html/pic.jpeg')
        scp.put('pic-p.jpeg','public_html/pic-p.jpeg')
        scp.close()
        return ImageSendMessage(
                original_content_url="https://stu-web.tkucs.cc/404411240/pic.jpeg",
                preview_image_url="https://stu-web.tkucs.cc/404411240/pic-p.jpeg"
                )
        