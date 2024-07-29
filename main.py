#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import asyncio
import log, my_httpd, tmdb_api, tvdb_api, tgbot
import os, time
import sender
from sender import Sender

AUTHOR = "xu4n_ch3n"
VERSION = "3.0.0"
UPDATETIME = "2024-07-29"
DESCRIPTION = "Emby Notifier is a media notification service for Emby Server. Now Jellyfin Server is alreay supported."
REPOSITORY = "https://github.com/Ccccx159/Emby_Notifier"

WELCOME = f"""
███████╗███╗   ███╗██████╗ ██╗   ██╗    ███╗   ██╗ ██████╗ ████████╗██╗███████╗██╗███████╗██████╗
██╔════╝████╗ ████║██╔══██╗╚██╗ ██╔╝    ████╗  ██║██╔═══██╗╚══██╔══╝██║██╔════╝██║██╔════╝██╔══██╗
█████╗  ██╔████╔██║██████╔╝ ╚████╔╝     ██╔██╗ ██║██║   ██║   ██║   ██║█████╗  ██║█████╗  ██████╔╝
██╔══╝  ██║╚██╔╝██║██╔══██╗  ╚██╔╝      ██║╚██╗██║██║   ██║   ██║   ██║██╔══╝  ██║██╔══╝  ██╔══██╗
███████╗██║ ╚═╝ ██║██████╔╝   ██║       ██║ ╚████║╚██████╔╝   ██║   ██║██║     ██║███████╗██║  ██║
╚══════╝╚═╝     ╚═╝╚═════╝    ╚═╝       ╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝
"""

CONTENT_STR = f"""
Welcome to Emby Notifier!
Author: {AUTHOR}
Version: {VERSION}
Update Time: {UPDATETIME}
Description: {DESCRIPTION}
Repository: {REPOSITORY}

"""

CONTENT = {
    "content": "Welcome to Emby Notifier!",
    "author": AUTHOR,
    "version": VERSION,
    "update_time": UPDATETIME,
    "intro": DESCRIPTION,
    "repo": REPOSITORY,
}


def welcome():
    print("\033[1;32m")
    print(WELCOME)
    print(f"\n{CONTENT_STR}")
    print("\033[0m")

def env_check():
    print(f"{'Checking environment variables...':<30}")
    print("\n--------Media Database info:")
    print(f"{'TMDB_API_TOKEN:':<15} {'(req)'} {os.getenv('TMDB_API_TOKEN', 'None')}")
    print(f"{'TVDB_API_KEY:':<15} {'(opt)'} {os.getenv('TVDB_API_KEY', 'None')}")
    print("\n--------Telegram Bot info:")
    print(f"{'TG_BOT_TOKEN:':<15} {'(req)'} {os.getenv('TG_BOT_TOKEN', 'None')}")
    print(f"{'TG_CHAT_ID:':<15} {'(req)'} {os.getenv('TG_CHAT_ID', 'None')}")
    print("\n--------Wechat App info:")
    print(f"{'WECHAT_CORP_ID:':<15} {'(req)'} {os.getenv('WECHAT_CORP_ID', 'None')}")
    print(f"{'WECHAT_CORP_SECRET:':<15} {'(req)'} {os.getenv('WECHAT_CORP_SECRET', 'None')}")
    print(f"{'WECHAT_AGENT_ID:':<15} {'(req)'} {os.getenv('WECHAT_AGENT_ID', 'None')}")
    print(f"{'WECHAT_USER_ID:':<15} {'(req)'} {os.getenv('WECHAT_USER_ID', 'None')}")
    print("\n--------Log info:")
    print(f"{'LOG_LEVEL:':<15} {'(opt)'} {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"{'LOG_EXPORT:':<15} {'(opt)'} {os.getenv('LOG_EXPORT', 'False')}")
    print(f"{'LOG_PATH:':<15} {'(opt)'} {os.getenv('LOG_PATH', '/var/tmp/emby_notifier_tg')}")

    # 检查媒体数据库信息
    try:
        if os.getenv('TMDB_API_TOKEN') is None:
            raise Exception("TMDB_API_TOKEN is required.")
        if os.getenv('TG_BOT_TOKEN') is None and os.getenv('WECHAT_CORP_ID') is None:
            raise Exception("You must set up at least one notification method, such as a Telegram bot or a WeChat Work application.")
        if os.getenv('TG_BOT_TOKEN') and os.getenv('TG_CHAT_ID') is None:
            raise Exception("TG_CHAT_ID is required.")
        if os.getenv('WECHAT_CORP_ID') and (os.getenv('WECHAT_CORP_SECRET') is None or os.getenv('WECHAT_AGENT_ID') is None or os.getenv('WECHAT_USER_ID') is None):
            raise Exception("Wechat Application config is not completed.")
    except Exception as e:
        log.logger.error(e)
        print("\033[1;31m")
        print("ERROR!!! Please set the required environment variables, and restart the service.")
        print("\033[0m")
        while True:
            time.sleep(1)

    if 'True' == os.getenv('LOG_EXPORT'):
        # 如果有日志文件输出，则向日志文件输出欢迎信息
        file_path = os.getenv('LOG_PATH', '/var/tmp/emby_notifier_tg/') + '/' + time.strftime("%Y-%m-%d", time.localtime()) + '.log'
        print(f"{WELCOME}\n{CONTENT_STR}", file=open(file_path, 'w'))
            

def require_check():
    log.logger.info("Checking requirements...")
    try:
        # check TMDB_API_TOKEN valid
        log.logger.info("Checking TMDB_API_TOKEN...")
        tmdb_api.login()
        
        # TODO: check TVDB_API_KEY valid
        # log.logger.info("Checking TVDB_API_KEY...")
        # token, err = tvdb_api.login()
        # if not token:
        #     raise Exception(err)
        
        # check TG_BOT_TOKEN valid
        log.logger.info("Checking TG_BOT_TOKEN...")
        tgbot.bot_authorization()
        
        # check TG_CHAT_ID valid
        log.logger.info("Checking TG_CHAT_ID...")
        tgbot.get_chat()

        # send welcome message
        global Sender
        sender.Sender = sender.SenderManager()
        sender.Sender.send_welcome(CONTENT)

    except Exception as e:
        log.logger.error(e)
        raise e



# 运行主事件循环
if __name__ == "__main__":
    welcome()
    env_check()
    require_check()
    asyncio.run(my_httpd.my_httpd())
