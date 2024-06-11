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

def bot_authorization():
    try:
        res = requests.get(TG_BOT_URL + "getMe")
        res.raise_for_status()
        log.logger.debug(log.SensitiveData(res.text))
        log.logger.info(f"Telegram bot authorization successful. Current bot: {res.json()['result']['username']}")
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Telegram bot authorization failed. Check network connection: {e}")
        raise e
    except Exception as e:
        log.logger.error(f"Telegram bot authorization failed. Error: {e}")
        raise e

def get_chat():
    payload = {
        "method": "getChat",
        "chat_id": TG_CHAT_ID,
    }
    try:
        res = requests.post(TG_BOT_URL, json=payload)
        res.raise_for_status()
        log.logger.debug(log.SensitiveData(res.text))
        chat_type = res.json()['result']['type']
        if chat_type == 'private':
            log.logger.info(f"Telegram getChat successful. Chat User: [{res.json()['result']['username']}], type: {chat_type}")
        elif chat_type == 'channel':
            log.logger.info(f"Telegram getChat successful. Chat title: [{res.json()['result']['title']}], type: {chat_type}")
        else:
            log.logger.warning(f"Telegram getChat successful. Chat type: {chat_type}, Chat Detail: {res.json()['result']}")
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Telegram getChat failed. Check network connection: {e}")
        raise e
    except Exception as e:
        log.logger.error(json.dumps(payload,ensure_ascii=False))
        log.logger.error(f"Telegram getChat failed. Error: {e}")
        raise e