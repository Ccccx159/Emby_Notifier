#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import asyncio
import my_httpd

# 运行主事件循环
if __name__ == "__main__":
    asyncio.run(my_httpd.my_httpd())
