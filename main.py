import asyncio
from datetime import datetime,date,timedelta
import random
import requests
import json,collections,xml
from lxml import etree
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import threading
import queue
from time import sleep

import blivedm

# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
    21452505
]

TEST_ROOM_ID = 21452505

wb_uid_list=[7198559139]
wb_name_list=['海海']

bili_uid_list=[434334701]
bili_name_list=['海海']

# 3215377 SC动态
# 3215378 微博/直播动态

sc_notify_channel = 3215377
nana7mi_notify_channel = 3215378

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

def messageSender():
    while True:
        message = messageQueue.get(block = True, timeout = None)
        send_guild_channel_msg(message)
        messageQueue.task_done()

async def main():
    global messageQueue
    messageQueue = queue.Queue(maxsize=-1) # infinity length
    senderThread = threading.Thread(target = messageSender)
    senderThread.start()
    await run_single_client()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(ListenWeibo, 'interval', seconds=61)
    scheduler.add_job(ListenLive, 'interval', seconds=37)
    scheduler.add_job(ListenDynamic, 'interval', seconds=61)
    scheduler.start()

async def ListenWeibo():
    print('查询微博动态...')
    for i in range(min(len(wb_uid_list),len(wb_name_list))):
        wb_content = GetWeibo(wb_uid_list[i], i)
        """
        content = '\n'.join(wb_content)
        if(content != ''):
            print('微博内容：'+content)
            # await send_qq_group_msg(271216120, content)
            await send_guild_channel_msg(49857441636955271, 1405378, content)
        """
        if(wb_content):
            for content in wb_content:
                # await send_qq_group_msg(271216120, content)
                # await send_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
                put_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
                print('微博内容：' + content)

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
        live_status = GetLiveStatus(roomid)
        if(live_status):
            print(bili_name_list[i] + '开播啦！\r\n直播间标题：' + live_status)
            # await send_guild_channel_msg(49857441636955271, nana7mi_notify_channel, bili_name_list[i] + '开播啦！\r\n直播间标题：' + live_status)
            put_guild_channel_msg(49857441636955271, nana7mi_notify_channel, bili_name_list[i] + '开播啦！\r\n直播间标题：' + live_status)

def GetLiveStatus(uid):
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
        dynamic_content = GetDynamicStatus(bili_uid_list[i], i)
        for content in dynamic_content:
            # await send_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
            put_guild_channel_msg(49857441636955271, nana7mi_notify_channel, content)
            print('动态内容：' + content)

def GetDynamicStatus(uid, biliindex):
    #print('Debug uid  '+str(uid))
    res = requests.get('https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid='+str(uid)+'&offset_dynamic_id=0')
    res.encoding='utf-8'
    res = res.text
    #res = res.encode('utf-8')
    cards_data = json.loads(res)
    try:
        cards_data = cards_data['data']['cards']
    except:
        exit()
    print('Success get')
    try:
        with open(str(uid)+'Dynamic','r') as f:
            last_dynamic_str = f.read()
            f.close()
    except Exception as err:
        last_dynamic_str=''
        pass
    if last_dynamic_str == '':
        last_dynamic_str = cards_data[1]['desc']['dynamic_id_str']
    print('last_dynamic_str: '+last_dynamic_str)
    index = 0
    content_list=[]
    cards_data[0]['card'] = json.loads(cards_data[0]['card'],encoding='gb2312')
    nowtime = time.time().__int__()
    # card是字符串，需要重新解析
    while last_dynamic_str != cards_data[index]['desc']['dynamic_id_str']:
        #print(cards_data[index]['desc'])
        try:
            # print('nowtime: ' + str(nowtime))
            # print('timestamp: ' + str(cards_data[index]['desc']['timestamp']))
            content = []
            if nowtime - cards_data[index]['desc']['timestamp'] > 59000000:
                break
            if (cards_data[index]['desc']['type'] == 64):
                content.append(bili_name_list[biliindex] +'发了新专栏「'+ cards_data[index]['card']['title'] + '」并说： ' +cards_data[index]['card']['dynamic'])
                content.append('\r\n')
            else:
                if (cards_data[index]['desc']['type'] == 8):
                    content.append(bili_name_list[biliindex] + '发了新视频「'+ cards_data[index]['card']['title'] + '」并说： ' +cards_data[index]['card']['dynamic'])
                    content.append('\r\n')
                else:         
                    if ('description' in cards_data[index]['card']['item']):
                        #这个是带图新动态
                        content.append(bili_name_list[biliindex] + '发了新动态： ' +cards_data[index]['card']['item']['description'])
                        content.append('\r\n')
                        #print('Fuck')
                        #CQ使用参考：[CQ:image,file=http://i1.piimg.com/567571/fdd6e7b6d93f1ef0.jpg]
                        for pic_info in cards_data[index]['card']['item']['pictures']:
                            content.append('[CQ:image,file='+pic_info['img_src']+']')
                            content.append('\r\n')
                    else:
                        #这个表示转发，原动态的信息在 cards-item-origin里面。里面又是一个超级长的字符串……
                        #origin = json.loads(cards_data[index]['card']['item']['origin'],encoding='gb2312') 我也不知道这能不能解析，没试过
                        #origin_name = 'Fuck'
                        if 'origin_user' in cards_data[index]['card']:
                            origin_name = cards_data[index]['card']['origin_user']['info']['uname']
                            content.append(bili_name_list[biliindex]+ '转发了「'+ origin_name + '」的动态并说： ' +cards_data[index]['card']['item']['content'])
                            content.append('\r\n')
                        else:
                            #这个是不带图的自己发的动态
                            content_list.append(bili_name_list[biliindex]+ '发了新动态： ' +cards_data[index]['card']['item']['content'])
                            content.append('\r\n')
            content.append('本条动态地址为'+'https://t.bilibili.com/'+ cards_data[index]['desc']['dynamic_id_str'])
            content_list.append(''.join(content))
        except Exception as err:
                print('PROCESS ERROR')
                print(str(err))
                # traceback.print_exc()
                pass
        index += 1
        if len(cards_data) == index:
            break
        cards_data[index]['card'] = json.loads(cards_data[index]['card'])
    f = open(str(uid)+'Dynamic','w')
    f.write(cards_data[0]['desc']['dynamic_id_str'])
    f.close()
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
        # await send_qq_group_msg(271216120, f'[{client.room_id}] 当前人气值：{message.popularity}')

    """
    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        # await send_qq_group_msg(271216120, f'[{client.room_id}] {message.uname}：{message.msg}')

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')
    """
    
    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')
        # await send_guild_channel_msg(49857441636955271, sc_notify_channel, f'醒目留言 ¥{message.price} {message.uname}：{message.message}')
        put_guild_channel_msg(49857441636955271, sc_notify_channel, f'醒目留言 ¥{message.price} {message.uname}：{message.message}')
        
# 1405112 直播讨论
# 1405378 七海动态
# 1392788 综合交流1区
# 1407656 其它vtb相关

def get_long_weibo( id):
    """获取长微博"""
    for i in range(5):
        url = 'https://m.weibo.cn/detail/%s' % id
        html = requests.get(url).text
        html = html[html.find('"status":'):]
        html = html[:html.rfind('"hotScheme"')]
        html = html[:html.rfind(',')]
        html = '{' + html + '}'
        js = json.loads(html, strict=False)
        weibo_info = js.get('status')
        if weibo_info:
            weibo = parse_weibo(weibo_info)
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

    text_body = weibo_info['text']
    selector = etree.HTML(text_body)
    weibo['text'] = etree.HTML(text_body).xpath('string(.)')
    weibo['article_url'] = get_article_url(selector)
    weibo['pics'] = get_pics(weibo_info)
    #return standardize_info(weibo)
    return weibo

def get_article_url(selector):
    """获取微博中头条文章的url"""
    article_url = ''
    text = selector.xpath('string(.)')
    if text.startswith(u'发布了头条文章'):
        url = selector.xpath('//a/@data-url')
        if url and url[0].startswith('http://t.cn'):
            article_url = url[0]
    return article_url

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

def GetWeibo(uid, wbindex):
    content_list=[]
    params = {
        'containerid': '107603' + str(uid)
    }
    url = 'https://m.weibo.cn/api/container/getIndex?'
    
    r = requests.get(url, params=params)
    res = r.json()
    if res['ok']:
        weibos = res['data']['cards']
        for w in weibos:
            if w['card_type'] == 9:
                retweeted_status = w['mblog'].get('retweeted_status')
                is_long = w['mblog'].get('isLongText')
                weibo_id = w['mblog']['id']
                weibo_url = w['scheme']
                weibo_avatar = w['mblog']['user']['avatar_hd']
                weibo_istop = w['mblog'].get('isTop')
                content = ['[CQ:image,file='+weibo_avatar+']']
                content.append('\r\n')
                created_time = get_created_time(w['mblog']['created_at'])
                if weibo_istop and weibo_istop == 1:
                    continue
                if datetime.now() - created_time > timedelta(seconds = 59):
                   break
                if retweeted_status and retweeted_status.get('id'):  # 转发
                    retweet_id = retweeted_status.get('id')
                    is_long_retweet = retweeted_status.get('isLongText')
                    if is_long:
                        weibo = get_long_weibo(weibo_id)
                        if not weibo:
                            weibo = parse_weibo(w['mblog'])
                    else:
                        weibo = parse_weibo(w['mblog'])
                    if is_long_retweet:
                        retweet = get_long_weibo(retweet_id)
                        if not retweet:
                            retweet = parse_weibo(retweeted_status)
                    else:
                        retweet = parse_weibo(retweeted_status)
                    weibo['retweet'] = retweet
                    content.append(wb_name_list[wbindex] + '在' + created_time.strftime("%Y-%m-%d %H:%M:%S") + '转发了微博并说：')
                    content.append('\r\n')
                    content.append(weibo['text'])
                    content.append('\r\n')
                    content.append('原微博：'+weibo['retweet']['text'])
                    content.append('\r\n')
                    content.append('本条微博地址是：' + weibo_url)
                    
                else:  # 原创
                    if is_long:
                        weibo = get_long_weibo(weibo_id)
                        if not weibo:
                            weibo = parse_weibo(w['mblog'])
                    else:
                        weibo = parse_weibo(w['mblog'])
                    content.append(wb_name_list[wbindex] + '在' + created_time.strftime("%Y-%m-%d %H:%M:%S") + '发了新微博并说：')
                    content.append('\r\n')
                    content.append(weibo['text'])
                    content.append('\r\n')
                    content.append('本条微博地址是：' + weibo_url)
                    for pic_info in weibo['pics']:
                        content.append('[CQ:image,file='+pic_info+']')
                content_list.append(''.join(content))
    return content_list

if __name__ == '__main__':
    asyncio.get_event_loop().create_task(main())
    asyncio.get_event_loop().run_forever()
