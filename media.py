#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import abc, json, time
import my_utils, tmdb_api, tvdb_api, tgbot
import log
import sender
from sender import Sender

from datetime import datetime


class IMedia(abc.ABC):

    def __init__(self):
        self.info_ = {
            "Name": "abc",
            "Type": "Movie/Episode",
            "PremiereYear": 1970,
            "ProviderIds": {"Tmdb": "123", "Imdb": "456", "Tvdb": "789"},
            "Series": 0,
            "Season": 0,
        }
        self.media_detail_ = {
            "server_type": "Emby/Jellyfin",
            "server_url": "https://emby.example.com",
            "server_name": "My_Emby_Server",
            "media_name": "movie_name",
            "media_type": "Movie/Episode",
            "media_rating": 0.0,
            "media_rel": "1970-01-01",
            "media_intro": "This is a movie/episode introduction.",
            "media_tmdburl": "https://www.themoviedb.org/movie(tv)/123456?language=zh-CN",
            "media_poster": "https://image.tmdb.org/t/p/w500/sFeFWK3SI662yC2sx4clmWttWVj.jpg",
            "media_backdrop": "https://image.tmdb.org/t/p/w500/sFeFWK3SI662yC2sx4clmWttWVj.jpg",
            "media_still": "https://image.tmdb.org/t/p/w500/sFeFWK3SI662yC2sx4clmWttWVj.jpg",
            "tv_season": 0,
            "tv_episode": 0,
            "tv_episode_name": "episode_name",
        }
        self.poster_ = ""
        self.server_name_ = ""
        self.escape_ch = ["_", "*", "`", "["]

    @abc.abstractmethod
    def parse_info(self, emby_media_info):
        pass

    @abc.abstractmethod
    def get_details(self):
        pass

    @abc.abstractmethod
    def send_caption(self):
        pass

    def _get_id(self):
        log.logger.info(json.dumps(self.info_, ensure_ascii=False))
        medias, err = tmdb_api.search_media(
            self.info_["Type"], self.info_["Name"], self.info_["PremiereYear"]
        )
        if err:
            log.logger.error(err)
            raise Exception(err)
        Tvdb_id = self.info_["ProviderIds"].get("Tvdb", "-1")
        for m in medias:
            ext_ids, err = tmdb_api.get_external_ids(self.info_["Type"], m["id"])
            if err:
                log.logger.warning(err)
                continue
            if Tvdb_id == str(ext_ids.get("tvdb_id")):
                self.info_["ProviderIds"]["Tmdb"] = str(m["id"])
                break
        if "Tmdb" not in self.info_["ProviderIds"]:
            log.logger.warn(f"No matched media found for {self.info_['Name']} {self.info_['PremiereYear']} in TMDB.")
            if self.info_["Type"] == "Movie":
                log.logger.warn(f"Use the first search result: {medias[0]['title']} {medias[0]['release_date'][:4]}.")
            else:
                log.logger.warn(f"Use the first search result: {medias[0]['original_name']} {medias[0]['first_air_date'][:4]}.")
            self.info_["ProviderIds"]["Tmdb"] = medias[0]["id"]


class Movie(IMedia):
    def __init__(self):
        super().__init__()
        self.info_["Type"] = "Movie"

    def __str__(self) -> str:
        return json.dumps(self.info_, ensure_ascii=False)

    def parse_info(self, emby_media_info):
        movie_item = emby_media_info["Item"]
        self.info_["Name"] = movie_item["Name"]
        self.info_["PremiereYear"] = (
            int(movie_item["PremiereDate"])
            if movie_item["PremiereDate"].isdigit()
            else (
                datetime.fromisoformat(
                    movie_item["PremiereDate"].replace("Z", "+00:00")
                ).year
                if my_utils.emby_version_check(emby_media_info["Server"]["Version"])
                else my_utils.iso8601_convert_CST(movie_item["PremiereDate"]).year
            )
        )
        self.info_["ProviderIds"] = movie_item["ProviderIds"]
        self.media_detail_["server_type"] = emby_media_info["Server"]["Type"]
        self.media_detail_["server_name"] = emby_media_info["Server"]["Name"]
        self.media_detail_["server_url"] = emby_media_info["Server"]["Url"]
        log.logger.debug(self.info_)

    def send_caption(self):
        sender.Sender.send_media_details(self.media_detail_)

    def get_details(self):
        if "Tmdb" not in self.info_["ProviderIds"]:
            self._get_id()

        movie_details, err = tmdb_api.get_movie_details(
            self.info_["ProviderIds"]["Tmdb"]
        )
        if err:
            log.logger.error(err)
            raise Exception(err)
        
        poster, err = tmdb_api.get_movie_poster(self.info_["ProviderIds"]["Tmdb"])
        if err:
            log.logger.error(err)
            raise Exception(err)
        
        backdrop, err = tmdb_api.get_movie_backdrop_path(self.info_["ProviderIds"]["Tmdb"])
        if err:
            log.logger.error(err)
            raise Exception(err)

        self.media_detail_["media_name"] = movie_details["title"]
        self.media_detail_["media_type"] = "Movie"
        self.media_detail_["media_rating"] = movie_details["vote_average"]
        self.media_detail_["media_rel"] = movie_details["release_date"]
        self.media_detail_["media_intro"] = movie_details["overview"]
        self.media_detail_["media_tmdburl"] = f"https://www.themoviedb.org/movie/{self.info_['ProviderIds']['Tmdb']}?language=zh-CN"
        self.media_detail_["media_poster"] = poster
        self.media_detail_["media_backdrop"] = backdrop
        log.logger.debug(self.media_detail_)


class Episode(IMedia):
    def __init__(self):
        super().__init__()
        self.info_["Type"] = "Episode"

    def __str__(self) -> str:
        return json.dumps(self.info_, ensure_ascii=False)

    def parse_info(self, emby_media_info):
        episode_item = emby_media_info["Item"]
        self.info_["Name"] = episode_item["SeriesName"]
        try:
            self.info_["PremiereYear"] = (
                int(episode_item["PremiereDate"])
                if episode_item["PremiereDate"].isdigit()
                else (
                    datetime.fromisoformat(
                        episode_item["PremiereDate"].replace("Z", "+00:00")
                    ).year
                    if my_utils.emby_version_check(emby_media_info["Server"]["Version"])
                    else my_utils.iso8601_convert_CST(episode_item["PremiereDate"]).year
                )
            )
        except Exception as e:
            log.logger.error(e)
            self.info_["PremiereYear"] = -1
        self.info_["ProviderIds"] = episode_item["ProviderIds"]
        self.info_["Series"] = episode_item["IndexNumber"]
        self.info_["Season"] = episode_item["ParentIndexNumber"]
        self.media_detail_["server_type"] = emby_media_info["Server"]["Type"]
        self.media_detail_["server_name"] = emby_media_info["Server"]["Name"]
        self.media_detail_["server_url"] = emby_media_info["Server"]["Url"]
        log.logger.debug(self.info_)

    def get_details(self):
        if "Tvdb" in self.info_["ProviderIds"]:
            tvdb_id, err = tvdb_api.get_seriesid_by_episodeid(self.info_["ProviderIds"]["Tvdb"])
            if err:
                log.logger.warn(err)
                self.info_["ProviderIds"].pop("Tvdb")
            else:
                self.info_["ProviderIds"]["Tvdb"] = str(tvdb_id)

        if "Tmdb" in self.info_["ProviderIds"]:
            # remove
            self.info_["ProviderIds"].pop("Tmdb")

        self._get_id()
        tv_details, err = tmdb_api.get_tv_episode_details(
            self.info_["ProviderIds"]["Tmdb"],
            self.info_["Season"],
            self.info_["Series"],
        )
        if err:
            log.logger.error(err)
            raise Exception(err)
        
        poster, err = tmdb_api.get_tv_season_poster(
            self.info_["ProviderIds"]["Tmdb"], self.info_["Season"]
        )
        if err:
            log.logger.error(err)
            raise Exception(err)
        
        still, err = tmdb_api.get_tv_episode_still_paths(self.info_["ProviderIds"]["Tmdb"], self.info_["Season"], self.info_["Series"])
        if err:
            log.logger.error(err)
            log.logger.warning("No still path found. use poster instead.")
            still = poster

        # tv_datails["air_date"] 为 None 时，查询season的air_date
        if tv_details["air_date"] is None:
            log.logger.warning("No air_date found for this episode, will use season air_date.")
            season_details, err = tmdb_api.get_tv_season_details(self.info_["ProviderIds"]["Tmdb"], self.info_["Season"])
            if season_details:
                tv_details["air_date"] = season_details["air_date"]
            else:
                log.logger.error(err)
                log.logger.warning("No air_date found for this episode, will use current year.")
                tv_details["air_date"] = str(datetime.now().year)
        
        self.media_detail_["media_name"] = self.info_["Name"]
        self.media_detail_["media_type"] = "Episode"
        self.media_detail_["media_rating"] = tv_details["vote_average"]
        self.media_detail_["media_rel"] = tv_details["air_date"]
        self.media_detail_["media_intro"] = tv_details["overview"]
        self.media_detail_["media_tmdburl"] = f"https://www.themoviedb.org/tv/{self.info_['ProviderIds']['Tmdb']}?language=zh-CN"
        self.media_detail_["media_poster"] = poster
        self.media_detail_["media_still"] = still
        self.media_detail_["tv_season"] = tv_details["season_number"]
        self.media_detail_["tv_episode"] = tv_details["episode_number"]
        self.media_detail_["tv_episode_name"] = tv_details["name"]
        log.logger.debug(self.media_detail_)


    def send_caption(self):
        sender.Sender.send_media_details(self.media_detail_)


def create_media(emby_media_info):
    if emby_media_info["Item"]["Type"] == "Movie":
        return Movie()
    elif emby_media_info["Item"]["Type"] == "Episode":
        return Episode()
    else:
        raise Exception("Unsupported media type.")


def jellyfin_msg_preprocess(msg):
    # jellyfin msg 部分字段中包含 "\n"，不处理会导致 json.loads() 失败
    if "\n" in msg:
        msg = msg.replace("\n", "")
    original_msg = json.loads(msg)
    # 通过字段 "NotificationType" 判断当前是否为 Jellyfin 事件
    if "NotificationType" in original_msg:
        if original_msg["NotificationType"] != "ItemAdded" or original_msg["ItemType"] not in ["Movie", "Episode"]:
            log.logger.warning(f"Unsupported event type: {original_msg['NotificationType'] or original_msg['ItemType']}")
            return None
        jellyfin_msg = {
            "Title": "event title",
            "Event": "library.new",
            "Item": {
                "Type": "Movie/Episode",
                "Name": "movie name",
                "SeriesName": "series name",
                "PremiereDate": "",
                "IndexNumber": 0,
                "ParentIndexNumber": 0,
                "ProviderIds": {},  # {"Tvdb": "5406258", "Imdb": "tt16116174", "Tmdb": "899082"}
            },
            "Server": {
                "Name": "server name",
                "Type": "Jellyfin",
                "Url": "Jellyfin server url",
            },
        }
        jellyfin_msg["Server"]["Name"] = original_msg["ServerName"]
        jellyfin_msg["Server"]["Type"] = "Jellyfin"
        jellyfin_msg["Server"]["Url"] = original_msg["ServerUrl"]
        jellyfin_msg["Event"] = "library.new"

        if original_msg["ItemType"] == "Movie":
            jellyfin_msg["Title"] = f"新 {original_msg['Name']} 在 {original_msg['ServerName']}"
            jellyfin_msg["Item"]["Type"] = "Movie"
            jellyfin_msg["Item"]["Name"] = original_msg["Name"]
        elif original_msg["ItemType"] == "Episode":
            jellyfin_msg["Title"] = f"新 {original_msg['SeriesName']} S{original_msg['SeasonNumber00']} - E{original_msg['EpisodeNumber00']} 在 {original_msg['ServerName']}"
            jellyfin_msg["Item"]["Type"] = "Episode"
            jellyfin_msg["Item"]["SeriesName"] = original_msg["SeriesName"]
            jellyfin_msg["Item"]["IndexNumber"] = original_msg["EpisodeNumber"]
            jellyfin_msg["Item"]["ParentIndexNumber"] = original_msg["SeasonNumber"]
        else:
            raise Exception("Unsupported media type.")

        jellyfin_msg["Item"]["PremiereDate"] = str(original_msg["Year"])
        if "Provider_tmdb" in original_msg:
            jellyfin_msg["Item"]["ProviderIds"]["Tmdb"] = original_msg["Provider_tmdb"]
        if "Provider_tvdb" in original_msg:
            jellyfin_msg["Item"]["ProviderIds"]["Tvdb"] = original_msg["Provider_tvdb"]
        if "Provider_imdb" in original_msg:
            jellyfin_msg["Item"]["ProviderIds"]["Imdb"] = original_msg["Provider_imdb"]
        # FIXME: Jellyfin 部分剧集没有提供 Provider_imdb 和 Provider_tvdb 信息
        if jellyfin_msg["Item"]["ProviderIds"] == {}:
            log.logger.warning(f"Jellyfin Server not get any ProviderIds for Event: {jellyfin_msg['Title']}")
        return jellyfin_msg
    else:
        original_msg["Server"]["Type"] = "Emby"
        # emby 推送的媒体信息不包含 server url，当前默认直接设置为 https://emby.media
        original_msg["Server"]["Url"] = "https://emby.media"
        return original_msg


def process_media(emby_media_info):
    emby_media_info = jellyfin_msg_preprocess(emby_media_info)
    if not emby_media_info:
        return
    log.logger.info(f"Received message: {emby_media_info['Title']}")
    if emby_media_info["Event"] != "library.new":
        log.logger.warning(f"Unsupported event type: {emby_media_info['Event']}")
        if emby_media_info["Event"] == "system.notificationtest":
            log.logger.warning("This is a notification test message. Please check your Telegram chat, if you received a message from Emby Notifier, it works!")
            sender.Sender.send_test_msg(
                f"🎉 *Congratulations!* 🎉 \n\nEmby Notifier worked! \n\nThis is a test message from *{emby_media_info['Server']['Name']}*! Now you can try adding a new media item to your Emby Server, whether it is a movie or a TV series~ \n\n{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
            )

        return
    try:
        md = create_media(emby_media_info)
        md.parse_info(emby_media_info)
        md.get_details()
        md.send_caption()
    except Exception as e:
        raise e
    else:
        log.logger.info(f"Message processing completed: {emby_media_info['Title']}")
