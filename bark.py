#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests, json, os
import time
import log


# server API, default is https://api.day.app
BARK_SERVER = os.getenv("BARK_SERVER", "https://api.day.app")
# single or multiple device keys, separated by commas
# e.g. "abcdefqweqwe,qwewqeqeqw,qweqweqweq,qweqweqwe"
BARK_DEVICE_KEYS = os.getenv("BARK_DEVICE_KEYS")
BARK_DEVICE_KEYS = BARK_DEVICE_KEYS.split(",")

def send_message(content: dict):
    if not BARK_SERVER or not BARK_DEVICE_KEYS:
        log.logger.error("Bark server or device keys not set.")
        return

    url = f"{BARK_SERVER}/push"
    # content 追加 device_keys
    content["device_keys"] = BARK_DEVICE_KEYS
    log.logger.warning(content)
    try:
        response = requests.post(url, json=content)
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Connection error: {e}")
        raise
    except Exception as e:
        log.logger.error(f"Error sending message: {e}")
        raise