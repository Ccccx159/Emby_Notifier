#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests, os, time
import log
import wxapp
import tgbot

Sender = None


class MessageSender:
    def send_welcome(self, welcome: dict):
        raise NotImplementedError

    def send_test_msg(self, test_content: str):
        raise NotImplementedError

    def send_media_details(self, media: dict):
        raise NotImplementedError


class TelegramSender(MessageSender):
    def send_welcome(self, welcome: dict):
        msg = f"{welcome['content']}\nAuthor: {welcome['author']}\nVersion: {welcome['version']}\nUpdate Time: {welcome['update_time']}\nDescription: {welcome['intro']}\nRepository: {welcome['repo']}\n"
        for ch in ["_", "*", "`", "["]:
            msg = msg.replace(ch, f"\\{ch}")
        tgbot.send_message(msg)

    def send_test_msg(self, test_content: str):
        for ch in ["_", "*", "`", "["]:
            test_content = test_content.replace(ch, f"\\{ch}")
        tgbot.send_message(test_content)

    def send_media_details(self, media: dict):
        caption = (
            "#影视更新 #{server_name}\n"
            + "\[{type_ch}]\n"
            + "片名： *{title}* ({year})\n"
            + "{episode}"
            + "评分： {rating}\n\n"
            + "上映日期： {rel}\n\n"
            + "内容简介： {intro}\n\n"
            + "相关链接： [TMDB]({tmdb_url})\n"
        )
        server_name = media["server_name"]
        for ch in ["_", "*", "`", "["]:
            server_name = server_name.replace(ch, f"\\{ch}")
        caption = caption.format(
            server_name=server_name,
            type_ch="电影" if media["media_type"] == "Movie" else "剧集",
            title=(
                media["media_name"]
                if media["media_type"] == "Movie"
                else f"{media['media_name']} {media['tv_episode_name']}"
            ),
            year=media["media_rel"][0:4],
            episode=(
                f"已更新至 第{media['tv_season']}季 第{media['tv_episode']}集\n"
                if media["media_type"] == "Episode"
                else ""
            ),
            rating=media["media_rating"],
            rel=media["media_rel"],
            intro=media["media_intro"],
            tmdb_url=media["media_tmdburl"],
        )
        poster = media["media_poster"]
        tgbot.send_photo(caption, poster)


class WechatAppSender(MessageSender):
    def send_welcome(self, welcome: dict):
        wxapp.send_welcome_card(welcome)

    def send_test_msg(self, test_content: str):
        wxapp.send_text(test_content)

    def send_media_details(self, media: dict):
        card_details = {
            "card_type": "news_notice",
            "source": {
                "icon_url": f"https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/{media.get('server_type', 'Emby').lower()}.png",
                "desc": f"{media.get('server_type')} Server",
                "desc_color": 0,
            },
            "main_title": {
                "title": f"#{media.get('server_name')} 影视更新",
            },
            "card_image": {
                "url": f"{media.get('media_backdrop') if media.get('media_type') == 'Movie' else media.get('media_still')}",
                "aspect_ratio": 2.25,
            },
            "vertical_content_list": [
                {
                    "title": f"[{'电影' if media.get('media_type') == 'Movie' else '剧集'}] {media.get('media_name')} ({media.get('media_rel')[:4]})"
                    + (
                        f" 第 {media.get('tv_season')} 季 | 第 {media.get('tv_episode')} 集"
                        if media.get("media_type") == "Episode"
                        else ""
                    ),
                    "desc": f"{media.get('media_intro')}",
                }
            ],
            "horizontal_content_list": [
                {"keyname": "上映日期", "value": f"{media.get('media_rel')}"},
                {"keyname": "评分", "value": f"{media.get('media_rating')}"},
            ],
            "jump_list": [
                {
                    "type": 1,
                    "url": f"{media.get('media_tmdburl')}",
                    "title": "TMDB",
                },
            ],
            "card_action": {"type": 1, "url": f"{media.get('server_url')}"},
        }
        wxapp.send_news_notice(card_details)


class SenderManager:
    def __init__(self):
        self.senders = []
        self._initialize_senders()

    def _initialize_senders(self):
        tg_bot_token = os.getenv("TG_BOT_TOKEN")
        tg_chat_id = os.getenv("TG_CHAT_ID")
        if tg_bot_token and tg_chat_id:
            self.senders.append(TelegramSender())

        wechat_corp_id = os.getenv("WECHAT_CORP_ID")
        wechat_corp_secret = os.getenv("WECHAT_CORP_SECRET")
        wechat_agent_id = os.getenv("WECHAT_AGENT_ID")
        if wechat_corp_id and wechat_corp_secret and wechat_agent_id:
            self.senders.append(WechatAppSender())

    def send_welcome(self, welcome_message: dict):
        for sender in self.senders:
            try:
                sender.send_welcome(welcome_message)
            except ValueError as e:
                print(f"Error sending welcome message: {e}")

    def send_test_msg(self, test_content):
        for sender in self.senders:
            sender.send_test_msg(test_content)

    def send_media_details(self, media):
        for sender in self.senders:
            sender.send_media_details(media)
