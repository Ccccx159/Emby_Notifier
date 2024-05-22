#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests, json, os
import log

# 填充电报机器人的token
TG_BOT_URL = "https://api.telegram.org/bot%s/" % os.getenv("TG_BOT_TOKEN")
# 填充电报频道 chat_id
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


def send_message(text):
    payload = {
        "method": "sendMessage",
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    log.logger.debug(log.SensitiveData(json.dumps(payload, ensure_ascii=False)))
    try:
        res = requests.post(TG_BOT_URL, json=payload)
        res.raise_for_status()
    except Exception as e:
        log.logger.error(json.dumps(payload,ensure_ascii=False))
        log.logger.error(res.text)
        raise e


def send_photo(caption, photo):
    payload = {
        "method": "sendPhoto",
        "chat_id": TG_CHAT_ID,
        "photo": photo,
        "caption": caption,
        "parse_mode": "Markdown",
    }
    log.logger.debug(log.SensitiveData(json.dumps(payload, ensure_ascii=False)))
    try:
        res = requests.post(TG_BOT_URL, json=payload)
        res.raise_for_status()
    except Exception as e:
        log.logger.error(json.dumps(payload,ensure_ascii=False))
        log.logger.error(res.text)
        raise e
