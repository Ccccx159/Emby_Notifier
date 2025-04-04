#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests, json, os
import time
import log


# 企业 id
CORP_ID = os.getenv("WECHAT_CORP_ID")
# 应用的凭证密钥
CORP_SECRET = os.getenv("WECHAT_CORP_SECRET")
# 应用的 agentid
AGENT_ID = int(os.getenv("WECHAT_AGENT_ID", "0"))

# 用户 id，推送给所有人时，设置为 "@all"
USER_ID = os.getenv("WECHAT_USER_ID", "@all")

# TOKEN
TOKEN = {
    "access_token": None,
    "expires_in": 7200,
    "expires_time": None,
}

TOKEN_FILE = "_tmp_wechat.json"

# 获取应用 token 的 url
GET_TOKEN_URL = (
    "https://qyapi.weixin.qq.com/cgi-bin/gettoken?"
    + f"corpid={CORP_ID}&corpsecret={CORP_SECRET}"
)

# 消息推送 url
SEND_MSG_URL = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="


def get_access_token():
    """
    Retrieves the access token required for authentication.

    Returns:
      str: The access token.

    Raises:
      requests.exceptions.ConnectionError: If there is a connection error.
      Exception: If there is an error retrieving the access token.
    """
    global TOKEN
    current_time = time.time()
    if TOKEN["access_token"] and TOKEN["expires_time"] > current_time:
        return TOKEN["access_token"]

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            TOKEN = json.load(f)
        if TOKEN["expires_time"] > current_time:
            return TOKEN["access_token"]

    try:
        res = requests.get(GET_TOKEN_URL)
        res.raise_for_status()
        if res.json()["errcode"] != 0:
            raise Exception(f"{res.text}")
        log.logger.debug(log.SensitiveData(res.text))
        # Update token
        TOKEN["access_token"] = res.json()["access_token"]
        TOKEN["expires_in"] = res.json()["expires_in"]
        TOKEN["expires_time"] = current_time + TOKEN["expires_in"]
        log.logger.info(
            f"Update access token successful. Token: {TOKEN['access_token']}"
        )

        with open(TOKEN_FILE, "w") as f:
            json.dump(TOKEN, f)

        return TOKEN["access_token"]
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Get access token failed. Check network connection: {e}")
        raise e
    except Exception as e:
        log.logger.error(f"Get access token failed. Error: {e}")
        raise e


def send_text(content):    
    payload = {
        "touser": USER_ID,
        "agentid": AGENT_ID,
        "safe": 0,
        "msgtype": "text",
        "text": {
            "content": content,
        },
    }
    log.logger.debug(log.SensitiveData(json.dumps(payload, ensure_ascii=False)))
    
    send_msg_url = SEND_MSG_URL + get_access_token()
    try:
        res = requests.post(send_msg_url, json=payload)
        res.raise_for_status()
        if res.json()["errcode"] != 0:
            raise Exception(res.text)
        log.logger.debug(f"Send text message successful. Response: {res.json()}")
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Send text message failed. Check network connection: {e}")
        raise e
    except Exception as e:
        log.logger.error(f"Send text message failed. Error: {e}")
        raise e



def send_markdown(content):
    payload = {
        "touser": USER_ID,
        "agentid": AGENT_ID,
        "safe": 0,
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        },
    }
    log.logger.debug(log.SensitiveData(json.dumps(payload, ensure_ascii=False)))

    send_msg_url = SEND_MSG_URL + get_access_token()
    try:
        res = requests.post(send_msg_url, json=payload)
        res.raise_for_status()
        if res.json()["errcode"] != 0:
            raise Exception(res.text)
        log.logger.debug(f"Send markdown message successful. Response: {res.json()}")
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Send markdown message failed. Check network connection: {e}")
        raise e
    except Exception as e:
        log.logger.error(f"Send markdown message failed. Error: {e}")
        raise e


def send_news(article):
    payload = {
        "touser": USER_ID,
        "agentid": AGENT_ID,
        "msgtype": "news",
        "news": {
            "articles": [article]    
        }
    }
    log.logger.debug(log.SensitiveData(json.dumps(payload, ensure_ascii=False)))

    send_msg_url = SEND_MSG_URL + get_access_token()
    try:
        res = requests.post(send_msg_url, json=payload)
        res.raise_for_status()
        if res.json()["errcode"] != 0:
            raise Exception(f"Send news failed. {res.text}")
        log.logger.debug(f"Send news successful. Response: {res.json()}")
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Send news failed. Check network connection: {e}")
        raise e
    except Exception as e:
        log.logger.error(f"Send news failed. Error: {e}")
        raise e


def send_news_notice(card_detail):    
    payload = {
        "touser": USER_ID,
        "agentid": AGENT_ID,
        "safe": 0,
        "msgtype": "template_card",
        "template_card": card_detail,
    }
    log.logger.debug(log.SensitiveData(json.dumps(payload, ensure_ascii=False)))

    send_msg_url = SEND_MSG_URL + get_access_token()
    try:
        res = requests.post(send_msg_url, json=payload)
        res.raise_for_status()
        if res.json()["errcode"] != 0:
            raise Exception(f"Send news notice failed. {res.text}")
        log.logger.debug(f"Send news notice successful. Response: {res.json()}")
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Send news notice failed. Check network connection: {e}")
        raise e
    except Exception as e:
        log.logger.error(f"Send news notice failed. Error: {e}")
        raise e


def send_welcome_card(welcome):
    payload = {
        "touser": USER_ID,
        "agentid": AGENT_ID,
        "safe": 0,
        "msgtype": "template_card",
        "template_card": {
            "card_type": "text_notice",
            "source": {
                "desc": "🚀 Emby Notifier",
                "desc_color": 0,
            },
            "main_title": {
                "title": f"🎉 {welcome['content']}",
            },
            "quote_area": {
                "quote_text": f"{welcome['intro']}",
            },
            "horizontal_content_list": [
                {"keyname": "Author", "value": f"{welcome['author']}"},
                {"keyname": "Version", "value": f"{welcome['version']}"},
                {"keyname": "Update Time", "value": f"{welcome['update_time']}"},
            ],
            "jump_list": [
                {
                    "type": 1,
                    "url": f"{welcome['repo']}",
                    "title": "👾 github",
                },
            ],
            "card_action": {
                "type": 1,
                "url": f"{welcome['repo']}",
            },
        },
    }
    log.logger.debug(log.SensitiveData(json.dumps(payload, ensure_ascii=False)))

    send_msg_url = SEND_MSG_URL + get_access_token()
    try:
        res = requests.post(send_msg_url, json=payload)
        res.raise_for_status()
        if res.json()["errcode"] != 0:
            raise Exception(f"{res.text}")
        log.logger.debug(f"Send news notice successful. Response: {res.json()}")
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"Send news notice failed. Check network connection: {e}")
        raise e
    except Exception as e:
        log.logger.error(f"Send news notice failed. Error: {e}")
        raise e
