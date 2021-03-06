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
import os
import sys
from time import sleep

def send_guild_channel_msg(message):
    response = requests.post("http://127.0.0.1:5700/send_guild_channel_msg", data = message, headers={'Connection':'close'})
    return response

def messageSend():
    message = {
        "guild_id":sys.argv[1],
        "channel_id":sys.argv[2],
        "message":sys.argv[3]
    }
    try:
        response = send_guild_channel_msg(message)
        logfile = open('sender_log','a', encoding = 'UTF-8')
        logfile.write(time.strftime('%Y-%m-%d %H:%M:%S\n',time.localtime(time.time())))
        logfile.write(str(response)+' '+response.text+'\n')
        logfile.close()
    except Exception as e:
        logfile = open('sender_log','a', encoding = 'UTF-8')
        logfile.write(time.strftime('%Y-%m-%d %H:%M:%S\n',time.localtime(time.time())))
        logfile.write(repr(e)+'\n')
        logfile.close()
        print(repr(e))
        os._exit(-1)
            
if __name__ == '__main__':
    messageSend()
