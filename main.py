import asyncio
from datetime import datetime,date,timedelta
import random
import requests
import json,collections,xml
from bs4 import BeautifulSoup
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import threading
import queue
import os
from time import sleep
from subprocess import run

from playwright.async_api import async_playwright

from PIL import Image, ImageFont, ImageDraw
import textwrap

import blivedm

# 微软雅黑的字体
path_to_ttf = 'font/msyh.ttc'
font = ImageFont.truetype(path_to_ttf, size=16, encoding='unic')

# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
    21452505
]

TEST_ROOM_ID = 21452505

wb_uid_list=[7198559139]
wb_name_list=['海海']
wb_cookie = ''
wb_ua = ''

bili_uid_list=[434334701]
bili_name_list=['海海']

danmaku_monitor_uid_list=[7706705, 14387072]

# 3215377 SC动态
# 3215378 微博/直播动态
# 1405112 直播讨论
# 1405378 七海动态
# 1392788 综合交流1区
# 1691384 综合交流2区
# 1407656 其它vtb相关
# 3217045 猎鲨队
# 4241211 禁言名单

sc_notify_channel = 3215377
nana7mi_notify_channel = 3215378
block_notify_channel = 4241211
live_discuss_channel = 1405112

async def send_qq_group_msg(group_id, message):
    data = {
        "group_id":group_id,
        "message":message,
        "auto_escape":"false"
    }
    response = requests.post("http://127.0.0.1:5700/send_group_msg", data = data)
    return response

def send_guild_channel_msg(guild_id, channel_id, message):
    # print(message)
    data = {
        "guild_id":guild_id,
        "channel_id":channel_id,
        "message":message
    }
    response = requests.post("http://127.0.0.1:5700/send_guild_channel_msg", data = data, headers={'Connection':'close'})
    return response

def send_guild_channel_msg(message):
    # print(message)
    response = requests.post("http://127.0.0.1:5700/send_guild_channel_msg", data = message, headers={'Connection':'close'})
    return response

def put_guild_channel_msg(guild_id, channel_id, message):
    # print(message)
    data = {
        "guild_id":guild_id,
        "channel_id":channel_id,
        "message":message
    }
    messageQueue.put(data)

"""
def messageSend(message):
    try:
        response = send_guild_channel_msg(message)
    except:
        print('消息发送失败，添加空格重试')
        sleep(0.03)
        message['message'] = message['message'] + ' '
        try:
            response = send_guild_channel_msg(message)
        except:
            print('消息发送失败，内容：' + message['message'])
            f = open('FailedMessage','a')
            f.write(message['message'] + '\n')
            f.close()
            sleep(0.01)
            os._exit(-1)
"""

# 一个中文字大小为16x16
"""
def pictureTransform(message):
    toPicture = []
    toRemove = []
    begLen = 0
    isBeg = True
    for content in message:
        if(content.startswith('[') == False):
            isBeg = False
            toPicture.append(content)
            toRemove.append(content)
        elif(isBeg == True):
            begLen = begLen + 1
    for content in toRemove:
        message.remove(content)
    toPicture = ''.join(toPicture)
    toPicture = textwrap.fill(text = toPicture, width = 20 ,drop_whitespace = False, replace_whitespace = False)
    img = Image.new(mode = 'RGB', size=(330, 10 + (22) * (toPicture.count('\n') + 1)), color = (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text(xy=(5,5), text=toPicture, font=font, fill=(0,0,0,255))
    img.save('C:\\TempPic\\output.png')
    message.insert(begLen, '[CQ:image,file=file:///C:\\TempPic\\output.png]')
"""

def doPicTrans(msg, index):
    msg = textwrap.fill(text = msg, width = 20 ,drop_whitespace = False, replace_whitespace = False)
    img = Image.new(mode = 'RGB', size=(330, 10 + (22) * (msg.count('\n') + 1)), color = (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text(xy=(5,5), text=msg, font=font, fill=(0,0,0,255))
    img.save('/home/wishcloud/Nana7mi_Monitor/TempPic/output'+str(index)+'.png')

def pictureTransform(message):
    toRemove = []
    toPicture = []
    i = 0
    while i < len(message):
        # print(message[i])
        if(message[i].startswith('[CQ')):
            if(len(toPicture) == 0):
                i = i + 1
                continue
            # 把之前toPicture里的转为图片
            # print('toPicture:'+''.join(toPicture))
            doPicTrans(''.join(toPicture), i)
            if(i > 0):
                message.insert(i - 1, '[CQ:image,file=file:////home/wishcloud/Nana7mi_Monitor/TempPic/output'+str(i)+'.png]')
                i = i + 1
            toPicture = []
        else:
            toPicture.append(message[i])
            toRemove.append(message[i])
        i = i + 1
    if(len(toPicture) > 0):
        # print('end toPicture:'+''.join(toPicture))
        doPicTrans(''.join(toPicture), len(message))
        message.append('[CQ:image,file=file:////home/wishcloud/Nana7mi_Monitor/TempPic/output'+str(len(message))+'.png]')
    for content in toRemove:
        message.remove(content)

def messageSender():
    while True:
        message = messageQueue.get(block = True, timeout = None)
        logfile = open('main_log','a', encoding = 'UTF-8')
        logfile.write(time.strftime('%Y-%m-%d %H:%M:%S\n',time.localtime(time.time())))
        try:
            logfile.write('消息内容：' + (''.join(message['message']))+'\n')
            code = os.WEXITSTATUS(os.system("python3 sender.pyw " + str(message['guild_id']) +' '+ str(message['channel_id']) +' "'+ ''.join(message['message'])+'"'))
            if code == 255:
                # logfile.write(repr(e) + '\n' + '消息发送失败，尝试加空格')
                # print(repr(e))
                logfile.write('消息发送失败，尝试加空格'+'\n')
                print('消息发送失败，尝试加空格')
                i = len(message['message']) - 1
                while i >= 0:
                    if(message['message'][i].startswith('[') == False):
                        message['message'][i] = message['message'][i] + ' '
                        break
                    i = i - 1
                
                code = os.WEXITSTATUS(os.system("python3 sender.pyw " + str(message['guild_id']) +' '+ str(message['channel_id']) +' "'+ ''.join(message['message'])+'"'))
                if code == 255:
                    # logfile.write(repr(e) + '\n' + '消息发送失败，尝试转换为图片')
                    # print(repr(e))
                    logfile.write('消息发送失败，尝试转换为图片'+'\n')
                    print('消息发送失败，尝试转换为图片')
                    originalMessage = ''.join(message['message'])
                    toMessage = message['message']
                    pictureTransform(toMessage)
                    code = os.WEXITSTATUS(os.system("python3 sender.pyw " + str(message['guild_id']) +' '+ str(message['channel_id']) +' "'+ ''.join(toMessage) +'"'))
                    if code == 255:
                        # print(repr(e))
                        print('该消息无法发送，已记录'+'\n')
                        f = open('FailedMessage','a', encoding = 'UTF-8')
                        # f.write(repr(e) + '\n')
                        f.write(originalMessage + '\n')
                        f.close()
        except Exception as e:
            logfile.write(repr(e))
        logfile.close()
        sleep(0.03)
        messageQueue.task_done()

def read_config():
    global wb_cookie
    global wb_ua
    try:
        with open('weibo_cookie.txt','r', encoding = 'UTF-8') as f:
            wb_cookie = f.read()
            f.close()
    except Exception as err:
            wb_cookie = ''
            pass
    try:
        with open('weibo_ua.txt','r', encoding = 'UTF-8') as f:
            wb_ua = f.read()
            f.close()
    except Exception as err:
            wb_ua = ''
            pass


async def main():
    global messageQueue
    messageQueue = queue.Queue(maxsize=-1) # infinity length
    
    senderThread = threading.Thread(target = messageSender)
    senderThread.start()
    
    await run_single_client()

    global last_weibo_time
    last_weibo_time = datetime.now()
    global last_dynamic_time
    last_dynamic_time = datetime.now()
    global last_comment_time
    last_comment_time = datetime.now()

    global wb_cookie
    global wb_ua
    read_config()
    print('wb_cookie:'+wb_cookie)
    print('wb_ua:'+wb_ua)
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(ListenWeibo, 'interval', seconds=57)
    scheduler.add_job(ListenLive, 'interval', seconds=53)
    scheduler.add_job(ListenDynamic, 'interval', seconds=61)
    scheduler.start()

async def ListenWeibo():
    print('查询微博动态...')
    for i in range(min(len(wb_uid_list),len(wb_name_list))):
        wb_content = None
        try:
            wb_content = await GetWeibo(wb_uid_list[i], i)
        except RequestsJSONDecodeError as e:
            print("JSON解码错误，可能是502错误")
        """
        content = '\n'.join(wb_content)
        if(content != ''):
            print('微博内容：'+content)
            # await send_qq_group_msg(271216120, content)
            await send_guild_channel_msg(49857441636955271, 1405378, content)
        """
        if(wb_content):
            for content in wb_content:
                # await send_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
                put_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
                print('微博内容：' + ''.join(content))

def get_live_room_id(mid):
    res = requests.get('https://api.bilibili.com/x/space/acc/info?mid='+str(mid)+'&jsonp=jsonp')
    res.encoding = 'utf-8'
    res = res.text
    data = json.loads(res)
    data = data['data']
    roomid = 0
    try:
        roomid = data['live_room']['roomid']
    except:
        pass
    return roomid

async def ListenLive():
    print('查询直播动态...')
    for i in range(len(bili_uid_list)):
        roomid = get_live_room_id(bili_uid_list[i])
        live_status = await GetLiveStatus(roomid)
        if(live_status):
            content = [bili_name_list[i] + '开播啦！\n直播间标题：' + live_status]
            print(content[0])
            # await send_guild_channel_msg(49857441636955271, nana7mi_notify_channel, bili_name_list[i] + '开播啦！\n直播间标题：' + live_status)
            put_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)

async def GetLiveStatus(uid):
    res = requests.get('https://api.live.bilibili.com/room/v1/Room/get_info?device=phone&;platform=ios&scale=3&build=10000&room_id=' + str(uid))
    #res = requests.get('https://api.live.bilibili.com/AppRoom/msg?room_id='+str(uid))
    #res = requests.get ('https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid=21463238')
    res.encoding = 'utf-8'
    res = res.text
    try:
        with open(str(uid)+'Live','r') as f:
            last_live_str = f.read()
            f.close()
    except Exception as err:
            last_live_str = '0'
            pass
    try:
        live_data = json.loads(res)
        live_data = live_data['data']
        now_live_status = str(live_data['live_status'])
        live_title = live_data['title']
    except:
        now_live_status = '0'
        pass
    f = open(str(uid)+'Live','w')
    f.write(now_live_status)
    f.close()
    if last_live_str != '1':
        if now_live_status == '1':
            return live_title
    return ''


async def ListenDynamic():
    print('查询B站动态...')
    for i in range(len(bili_uid_list)):
        dynamic_content = await GetDynamicStatus(bili_uid_list[i], i)
        for content in dynamic_content:
            # await send_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
            put_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
            print('动态内容：' + ''.join(content))

async def GetDynamicContent(dynamic_id):
    async with async_playwright() as p:
        browser = await p.webkit.launch()
        device = p.devices['iPhone 12 Pro']
        context = await browser.new_context(
            **device
            )
        page = await context.new_page()
        await page.set_viewport_size({'width':560, 'height':3500})
        await page.goto('https://m.bilibili.com/dynamic/'+dynamic_id)
        await page.locator('#app > div > div.up-archive').scroll_into_view_if_needed()
        pic_path = '/home/wishcloud/Nana7mi_Monitor/TempPic/dynamic_'+dynamic_id+'_screenshot.png'
        await page.locator('#app > div > div.launch-app-btn.card-wrap > div').screenshot(path=pic_path)
        await browser.close()
        return pic_path

async def GetDynamicStatus(uid, biliindex):
    #print('Debug uid  '+str(uid))
    global last_dynamic_time
    print('last_dynamic_time:'+last_dynamic_time.strftime("%Y-%m-%d %H:%M:%S"))
    headers = {
        'Referer': 'https://space.bilibili.com/{user_uid}/'.format(user_uid=uid)
    }
    res = requests.get('https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid='+str(uid)+'&offset_dynamic_id=0', headers=headers)
    res.encoding='utf-8'
    res = res.text
    #res = res.encode('utf-8')
    cards_data = json.loads(res)
    try:
        cards_data = cards_data['data']['cards']
    except:
        exit()
    # print('Success get')
    index = 0
    content_list=[]
    cards_data[0]['card'] = json.loads(cards_data[0]['card'],encoding='gb2312')

    now_dynamic_time = last_dynamic_time
    # card是字符串，需要重新解析
    while index < len(cards_data):
        #print(cards_data[index]['desc'])
        try:
            dynamic_id = cards_data[index]['desc']['dynamic_id_str']
            # print('nowtime: ' + str(nowtime))
            # print('timestamp: ' + str(cards_data[index]['desc']['timestamp']))
            content = []
            created_time = datetime.fromtimestamp(int(cards_data[index]['desc']['timestamp']))
            if not (last_dynamic_time < created_time): # 不是新动态
                break
            # 以下是处理新动态的内容
            if now_dynamic_time < created_time:
                 now_dynamic_time = created_time
            
            pic_path = await GetDynamicContent(dynamic_id)
            content.append('[CQ:image,file=file:///'+pic_path+']')
            content.append('\n')
            """
            if (cards_data[index]['desc']['type'] == 64):
                content.append(bili_name_list[biliindex] +'发了新专栏「'+ cards_data[index]['card']['title'] + '」并说： ' +cards_data[index]['card']['dynamic'])
                content.append('\n')
            else:
                if (cards_data[index]['desc']['type'] == 8):
                    content.append(bili_name_list[biliindex] + '发了新视频「'+ cards_data[index]['card']['title'] + '」并说： ' +cards_data[index]['card']['dynamic'])
                    content.append('\n')
                else:         
                    if ('description' in cards_data[index]['card']['item']):
                        #这个是带图新动态
                        content.append(bili_name_list[biliindex] + '发了新动态： ' +cards_data[index]['card']['item']['description'])
                        content.append('\n')
                        #print('Fuck')
                        #CQ使用参考：[CQ:image,file=http://i1.piimg.com/567571/fdd6e7b6d93f1ef0.jpg]
                        for pic_info in cards_data[index]['card']['item']['pictures']:
                            content.append('[CQ:image,file='+pic_info['img_src']+']')
                            content.append('\n')
                    else:
                        #这个表示转发，原动态的信息在 cards-item-origin里面。里面又是一个超级长的字符串……
                        #origin = json.loads(cards_data[index]['card']['item']['origin'],encoding='gb2312') 我也不知道这能不能解析，没试过
                        #origin_name = 'Fuck'
                        if 'origin_user' in cards_data[index]['card']:
                            origin_name = cards_data[index]['card']['origin_user']['info']['uname']
                            content.append(bili_name_list[biliindex]+ '转发了「'+ origin_name + '」的动态并说： ' +cards_data[index]['card']['item']['content'])
                            content.append('\n')
                        else:
                            #这个是不带图的自己发的动态
                            content_list.append(bili_name_list[biliindex]+ '发了新动态： ' +cards_data[index]['card']['item']['content'])
            """
            content.append('本条动态地址为'+'https://m.bilibili.com/dynamic/'+ cards_data[index]['desc']['dynamic_id_str'])
            content_list.append(content)
        except Exception as err:
                print('PROCESS ERROR')
                print(str(err))
                # traceback.print_exc()
                pass
        index += 1
        if len(cards_data) == index:
            break
        cards_data[index]['card'] = json.loads(cards_data[index]['card']) # 加载下一条动态
    # 更新last_dynamic_time
    print('now_dynamic_time:'+now_dynamic_time.strftime("%Y-%m-%d %H:%M:%S"))
    last_dynamic_time = now_dynamic_time
    return content_list


async def run_single_client():
    """
    监听一个直播间
    """
    room_id = TEST_ROOM_ID
    # 如果SSL验证失败就把ssl设为False，B站真的有过忘续证书的情况
    client = blivedm.BLiveClient(room_id, ssl=True)
    handler = MyHandler()
    client.add_handler(handler)

    client.start()

async def run_multi_client():
    """
    同时监听多个直播间
    """
    clients = [blivedm.BLiveClient(room_id) for room_id in TEST_ROOM_IDS]
    handler = MyHandler()
    for client in clients:
        client.add_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))

class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
        # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa
    
    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        print(f'[{client.room_id}] 当前人气值：{message.popularity}')
        # content = [f'当前人气值：{message.popularity}']
        # put_guild_channel_msg(49857441636955271, sc_notify_channel, content)

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        # print(f'[{client.room_id}] {message.uname}：{message.msg}')
        if(danmaku_monitor_uid_list.count(message.uid) > 0):
            content = [f'{message.uname}在海海直播间发送了弹幕：{message.msg}']
            print(content[0])
            put_guild_channel_msg(49857441636955271, live_discuss_channel, content)
        elif(message.uid == 434334701):
            content = [f'{message.uname}在直播间发送了弹幕：{message.msg}']
            print(content[0])
            put_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
        
    """
    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')
    """
    
    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        # print(f" - $ $ $ - \n「`七海Nana7mi`收到了`{message.uname}`发送了{message.price}块 SC:`{message.message}`」")
        content = ['---------------\n', f'醒目留言 ¥{message.price} {message.uname}：{message.message}', '\n---------------']
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')
        # await send_guild_channel_msg(49857441636955271, sc_notify_channel, f'醒目留言 ¥{message.price} {message.uname}：{message.message}')
        put_guild_channel_msg(49857441636955271, sc_notify_channel, content)
        # put_guild_channel_msg(49857441636955271, live_discuss_channel, content)

    async def _on_room_block(self, client: blivedm.BLiveClient, message: blivedm.RoomBlockMessage):
        content = [f'恭喜{message.uname}(uid：{message.uid})在海海直播间被拉黑了']
        put_guild_channel_msg(49857441636955271, block_notify_channel, content)

def get_long_weibo(weibo_id, headers):
    """获取长微博"""
    for i in range(3):
        url = 'https://m.weibo.cn/detail/' + weibo_id
        print('url: '+url)
        html = requests.get(url, headers = headers).text
        html = html[html.find('"status":'):]
        html = html[:html.rfind('"hotScheme"')]
        html = html[:html.rfind(',')]
        html = '{' + html + '}'
        js = json.loads(html, strict=False)
        weibo_info = js.get('status')
        if weibo_info:
            weibo = parse_weibo(weibo_info)
            #截短长微博
            if(len(weibo['text']) > 100):
                weibo['text'] = weibo['text'][0:97] + "..."
            print('after cut: ' + weibo['text'])
            return weibo
        time.sleep(random.randint(6, 10))


def parse_weibo(weibo_info):
    weibo = collections.OrderedDict()
    if weibo_info['user']:
        weibo['user_id'] = weibo_info['user']['id']
        weibo['screen_name'] = weibo_info['user']['screen_name']
    else:
        weibo['user_id'] = ''
        weibo['screen_name'] = ''

    weibo['text'] = parse_text(weibo_info['text'])[0]

    weibo['pics'] = get_pics(weibo_info)
    #return standardize_info(weibo)
    return weibo

def get_pics(weibo_info):
    """获取微博原始图片url"""
    if weibo_info.get('pics'):
        pic_info = weibo_info['pics']
        pic_list = [pic['large']['url'] for pic in pic_info]
        # pics = ','.join(pic_list)
    else:
        pic_list = []
    return pic_list

def get_created_time(created_at):
    """
    标准化微博发布时间
    if u"刚刚" in created_at:
        created_at = datetime.now()
    elif u"分钟" in created_at:
        minute = created_at[:created_at.find(u"分钟")]
        minute = timedelta(minutes=int(minute))
        created_at = datetime.now() - minute
    elif u"小时" in created_at:
        hour = created_at[:created_at.find(u"小时")]
        hour = timedelta(hours=int(hour))
        created_at = datetime.now() - hour
    elif u"昨天" in created_at:
        day = timedelta(days=1)
        created_at = datetime.now() - day
    elif created_at.count('-') == 1:
        created_at = datetime.now() - timedelta(days=365)
    """
    created_at = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
    created_at = created_at.replace(tzinfo=None)
    # print(created_at)
    return created_at

def parse_text(wb_text):
    wb_soup = BeautifulSoup(wb_text, features="lxml")
    # print(wb_soup)

    all_a = wb_soup.findAll('a')
    pic_list = []
    for a in all_a:
        # print('a:'+str(a))
        pic_link = a.get('href')
        if pic_link == None:
            pic_link = a.getText()
            a.replaceWith(pic_link)
        else:
            # 判断是否为图片
            if pic_link.endswith('.jpg') or pic_link.endswith('.jpeg') or pic_link.endswith('.png') or pic_link.endswith('.gif'):
                # 写入cq码
                # print('[CQ:image,file='+pic_link+']')
                pic_list.append('[CQ:image,file='+pic_link+']')
                a.extract()
            else: # 不是图片
                # 是at
                if a.getText().startswith('@'):
                    pic_link = a.getText()
                a.replaceWith(pic_link)
                

    all_img = wb_soup.findAll('img')
    for img in all_img:
        img_desc = img.get('alt')
        if img_desc == None:
            img_desc = img.getText()
        img.replaceWith(img_desc)

    res = []
    res.append(wb_soup.getText())
    res.append(pic_list)
    
    return res

# 记录下最晚一条被发送的评论的时间
# 爬取按热度排序的第一页评论，如果有符合条件的就发送
# 爬取评论的楼中楼评论，如果有符合条件的就发送
async def GetWeiboComment(weibo_id, mid, headers, uid, content_list, wbindex, weibo_url):
    await asyncio.sleep(random.randint(2, 5))
    url = 'https://m.weibo.cn/comments/hotflow?'
    params = {
        'id': weibo_id,
        'mid': mid,
        'max_id_type': '0'
    }
    r = requests.get(url, params=params, headers=headers)
    res = r.json()
    global last_comment_time
    now_comment_time = last_comment_time
    if res['ok']: # ok为0代表没有评论
        comments = res['data']['data']
        if not comments:
            print('no comment')
            return now_comment_time
        for comment in comments:
            # 符合条件的评论，发送并爬取楼中楼
            # 预先处理，去掉xml
            comment_with_pic = parse_text(comment['text'])
            comment['text'] = comment_with_pic[0]
            comment_pic_list = comment_with_pic[1]
            if comment.get('pic'):
                comment_pic_list.append('[CQ:image,file='+comment['pic']['large']['url']+']')
            
            comment_created_time = get_created_time(comment['created_at'])
            if comment['user']['id'] == uid and last_comment_time < comment_created_time:
                content = []
                # 更新时间记录
                if now_comment_time < comment_created_time:
                    now_comment_time = comment_created_time
                content.append(wb_name_list[wbindex] + '在' + comment_created_time.strftime("%Y-%m-%d %H:%M:%S") + '发了新评论并说：')
                content.append('\n')
                content.append(comment['text'])
                content.append('\n')
                content.append('原微博地址：'+weibo_url)
                content.append('\n')
                for pic in comment_pic_list:
                    content.append(pic)
                content_list.append(content)
            # 不符合条件的评论，只爬取楼中楼
            # print(type(comment['comments']))
            if not comment['comments']: # 是否存在楼中楼
                continue
            for inner_comment in comment['comments']:
                # print(inner_comment)
                inner_comment_created_time = get_created_time(inner_comment['created_at'])
                if inner_comment['user']['id'] == uid and last_comment_time < inner_comment_created_time:
                    content = []
                    # 更新时间记录
                    if now_comment_time < inner_comment_created_time:
                        now_comment_time = inner_comment_created_time
                    content.append(wb_name_list[wbindex] + '在' + inner_comment_created_time.strftime("%Y-%m-%d %H:%M:%S") + '回复了一条评论并说：')
                    content.append('\n')

                    # 去除xml
                    inner_comment_with_pic = parse_text(inner_comment['text'])
                    inner_comment['text'] = inner_comment_with_pic[0]
                    inner_comment_pic_list = inner_comment_with_pic[1]
                    if inner_comment.get('pic'):
                        inner_comment_pic_list.append('[CQ:image,file='+inner_comment['pic']['large']['url']+']')
                    
                    content.append(inner_comment['text'])
                    content.append('\n')
                    content.append('原评论内容：'+comment['text'])
                    content.append('\n')
                    # 加入回复评论的图片
                    for pic in comment_pic_list:
                        content.append(pic)
                        
                    content.append('\n')
                    content.append('原微博地址：'+weibo_url)
                    content.append('\n')
                    for pic in inner_comment_pic_list:
                        content.append(pic)
                    content_list.append(content)
        # 更新最晚时间
        print('now_comment_time:'+now_comment_time.strftime("%Y-%m-%d %H:%M:%S"))
        # last_comment_time = now_comment_time
    else:
        print("no comment!")
    return now_comment_time

async def GetWeibo(uid, wbindex):
    global last_weibo_time
    print('last_weibo_time:'+last_weibo_time.strftime("%Y-%m-%d %H:%M:%S"))
    global last_comment_time
    print('last_comment_time:'+last_comment_time.strftime("%Y-%m-%d %H:%M:%S"))
    content_list=[]
    params = {
        'containerid': '107603' + str(uid)
    }
    url = 'https://m.weibo.cn/api/container/getIndex?'

    headers = {
        'Cookie': wb_cookie,
        'User-Agent': wb_ua
    }
    r = requests.get(url, params=params, headers=headers)
    res = r.json()
    if res['ok']:
        weibos = res['data']['cards']
        # 初值
        now_weibo_time = last_weibo_time
        now_comment_time = last_comment_time
        for i in range(min(len(weibos), 5)):
            w = weibos[i]
            if w['card_type'] == 9:
                retweeted_status = w['mblog'].get('retweeted_status')
                is_long = w['mblog'].get('isLongText')
                weibo_id = w['mblog']['id']
                mid = w['mblog']['mid']
                # 获取用户简介
                user_desc = w['mblog']['user']['description']
                
                weibo_url = 'https://m.weibo.cn/detail/' + weibo_id
                weibo_avatar = w['mblog']['user']['avatar_hd']
                weibo_istop = w['mblog'].get('isTop')
                content = ['[CQ:image,file='+weibo_avatar+']']
                content.append('\n')
                created_time = get_created_time(w['mblog']['created_at'])
                # 保存要插入在content_list中的位置
                content_index = len(content_list)
                # 查询楼中楼
                comment_created_time = await GetWeiboComment(weibo_id, mid, headers, uid, content_list, wbindex, weibo_url)
                if now_comment_time < comment_created_time:
                    now_comment_time = comment_created_time
                """
                if weibo_istop and weibo_istop == 1:
                    # 如果置顶微博在上一次查询之后发出，则需要发送
                    if datetime.now() - created_time > timedelta(seconds = 69000):
                        continue
                else:
                    # 记录除置顶以外最新一条微博id
                    if now_weibo_id == '':
                        now_weibo_id = weibo_id
                if datetime.now() - created_time > timedelta(seconds = 69000):
                    break
                if last_weibo_id == weibo_id:
                    break;
                """
                if not (last_weibo_time < created_time): # 不是新微博
                    continue
                # 以下是处理新微博的部分
                # 记录最晚一条微博的时间
                if now_weibo_time < created_time:
                    now_weibo_time = created_time
                if retweeted_status and retweeted_status.get('id'):  # 转发
                    retweet_id = retweeted_status.get('id')
                    is_long_retweet = retweeted_status.get('isLongText')
                    if is_long:
                        weibo = get_long_weibo(weibo_id, headers)
                        if not weibo:
                            weibo = parse_weibo(w['mblog'])
                    else:
                        weibo = parse_weibo(w['mblog'])
                    if is_long_retweet:
                        retweet = get_long_weibo(retweet_id, headers)
                        if not retweet:
                            retweet = parse_weibo(retweeted_status)
                    else:
                        retweet = parse_weibo(retweeted_status)
                    weibo['retweet'] = retweet
                    content.append(wb_name_list[wbindex] + '在' + created_time.strftime("%Y-%m-%d %H:%M:%S") + '转发了微博并说：')
                    content.append('\n')
                    content.append(weibo['text'])
                    content.append('\n')
                    content.append('原微博：'+weibo['retweet']['text'])
                    content.append('\n')
                    # 添加原微博的图片
                    for pic_info in weibo['retweet']['pics']:
                        content.append('[CQ:image,file='+pic_info+']')
                    content.append('\n')
                    content.append('本条微博地址是：' + weibo_url)
                    
                else:  # 原创
                    if is_long:
                        weibo = get_long_weibo(weibo_id, headers)
                        if not weibo:
                            weibo = parse_weibo(w['mblog'])
                    else:
                        weibo = parse_weibo(w['mblog'])
                    content.append(wb_name_list[wbindex] + '在' + created_time.strftime("%Y-%m-%d %H:%M:%S") + '发了新微博并说：')
                    content.append('\n')
                    content.append(weibo['text'])
                    content.append('\n')
                    content.append('本条微博地址是：' + weibo_url)
                    content.append('\n')
                    for pic_info in weibo['pics']:
                        content.append('[CQ:image,file='+pic_info+']')
                content_list.insert(content_index, content)
    print('now_weibo_time:'+now_weibo_time.strftime("%Y-%m-%d %H:%M:%S"))
    # 更新last_weibo_time
    last_weibo_time = now_weibo_time
    last_comment_time = now_comment_time
    UpdateUserDesc(wbindex, user_desc)
    return content_list

def UpdateUserDesc(wbindex, user_desc):
    uid = wb_uid_list[wbindex]
    try:
        with open(str(uid)+'WeiboDesc','r', encoding='UTF-8') as f:
            last_user_desc = f.read()
            f.close()
    except Exception as err:
            last_user_desc = ''
            print(repr(err))
            return
    if (user_desc != last_user_desc):
        content = [wb_name_list[wbindex] + '把简介从\n' + last_user_desc + '\n' + '改成了\n' + user_desc]
        put_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
        try:
            with open(str(uid)+'WeiboDesc','w', encoding='UTF-8') as f:
                f.write(user_desc)
                f.close()
        except Exception as err:
                pass
        

if __name__ == '__main__':
    asyncio.get_event_loop().create_task(main())
    asyncio.get_event_loop().run_forever()
