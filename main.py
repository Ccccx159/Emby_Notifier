#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import asyncio
import my_httpd
import os, time

def welcome():
    print("\033[1;32m")
    print("""
███████╗███╗   ███╗██████╗ ██╗   ██╗    ███╗   ██╗ ██████╗ ████████╗██╗███████╗██╗███████╗██████╗ 
██╔════╝████╗ ████║██╔══██╗╚██╗ ██╔╝    ████╗  ██║██╔═══██╗╚══██╔══╝██║██╔════╝██║██╔════╝██╔══██╗
█████╗  ██╔████╔██║██████╔╝ ╚████╔╝     ██╔██╗ ██║██║   ██║   ██║   ██║█████╗  ██║█████╗  ██████╔╝
██╔══╝  ██║╚██╔╝██║██╔══██╗  ╚██╔╝      ██║╚██╗██║██║   ██║   ██║   ██║██╔══╝  ██║██╔══╝  ██╔══██╗
███████╗██║ ╚═╝ ██║██████╔╝   ██║       ██║ ╚████║╚██████╔╝   ██║   ██║██║     ██║███████╗██║  ██║
╚══════╝╚═╝     ╚═╝╚═════╝    ╚═╝       ╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝
          """)
    print("\033[0m")
    print("Welcome to Emby Notifier!")
    print("Author: xu4n_ch3n")
    print("Version: 1.0.4")
    print("Date: 2024-05-16")
    print("Description: Emby Notifier is a media notification service for Emby Server. ")
    print("Repository: https://github.com/Ccccx159/Emby_Notifier")
    print("")

def env_check():
    print(f"{'Checking environment variables...':<30}")
    print(f"{'TMDB_API_TOKEN:':<15} {'(req)'} {os.getenv('TMDB_API_TOKEN', 'None')}")
    print(f"{'TVDB_API_KEY:':<15} {'(req)'} {os.getenv('TVDB_API_KEY', 'None')}")
    print(f"{'TG_BOT_TOKEN:':<15} {'(req)'} {os.getenv('TG_BOT_TOKEN', 'None')}")
    print(f"{'TG_CHAT_ID:':<15} {'(req)'} {os.getenv('TG_CHAT_ID', 'None')}")
    print(f"{'LOG_LEVEL:':<15} {'(opt)'} {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"{'LOG_EXPORT:':<15} {'(opt)'} {os.getenv('LOG_EXPORT', 'False')}")
    print(f"{'LOG_PATH:':<15} {'(opt)'} {os.getenv('LOG_PATH', '/var/tmp/emby_notifier_tg')}")

    if os.getenv('TMDB_API_TOKEN') is None or os.getenv('TVDB_API_KEY') is None or os.getenv('TG_BOT_TOKEN') is None or os.getenv('TG_CHAT_ID') is None:
        print("\033[1;31m")
        print("ERROR!!! Please set the required environment variables, and restart the service.")
        print("\033[0m")
        while True:
            time.sleep(1)
            


# 运行主事件循环
if __name__ == "__main__":
    welcome()
    env_check()
    asyncio.run(my_httpd.my_httpd())
