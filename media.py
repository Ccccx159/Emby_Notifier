#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import abc, json
import my_utils, tmdb_api, tvdb_api, tgbot
import log

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
        self.caption_ = (
            "#影视更新 #{server_name}\n"
            + "\[{type_ch}]\n"
            + "片名： *{title}* ({year})\n"
            + "{episode}"
            + "评分： {rating}\n\n"
            + "上映日期： {rel}\n\n"
            + "内容简介： {intro}\n\n"
            + "相关链接： [TMDB](https://www.themoviedb.org/{type}/{tmdbid}?language=zh-CN)\n"
        )
        self.poster_ = ""
        self.server_name_ = ""
        self.escape_ch = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    @abc.abstractmethod
    def parse_info(self, emby_media_info):
        pass

    @abc.abstractmethod
    def get_caption(self):
        pass

    @abc.abstractmethod
    def get_poster(self):
        pass

    @abc.abstractmethod
    def send_caption(self):
        pass

    def _get_id(self):
        log.logger.debug(json.dumps(self.info_, ensure_ascii=False))
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
            else my_utils.iso8601_convert_CST(movie_item["PremiereDate"]).year
        )
        self.info_["ProviderIds"] = movie_item["ProviderIds"]
        self.server_name_ = emby_media_info["Server"]["Name"]
        log.logger.debug(self.info_)

    def get_caption(self):
        if "Tmdb" not in self.info_["ProviderIds"]:
            self._get_id()

        movie_details, err = tmdb_api.get_movie_details(
            self.info_["ProviderIds"]["Tmdb"]
        )
        if err:
            log.logger.error(err)
            raise Exception(err)
        
        # check server name and escape any special characters
        for ch in self.escape_ch:
            self.server_name_ = self.server_name_.replace(ch, "\\" + ch)

        self.caption_ = self.caption_.format(
            server_name=self.server_name_,
            type_ch="电影",
            title=movie_details["title"],
            year=movie_details["release_date"][:4],
            episode="",
            rating=movie_details["vote_average"],
            rel=movie_details["release_date"],
            intro=movie_details["overview"],
            type="movie",
            tmdbid=self.info_["ProviderIds"]["Tmdb"],
        )
        log.logger.debug(self.caption_)

    def get_poster(self):
        self.poster_, err = tmdb_api.get_movie_poster(self.info_["ProviderIds"]["Tmdb"])
        if err:
            log.logger.error(err)
            raise Exception(err)

    def send_caption(self):
        tgbot.send_photo(self.caption_, self.poster_)


class Episode(IMedia):
    def __init__(self):
        super().__init__()
        self.info_["Type"] = "Episode"

    def __str__(self) -> str:
        return json.dumps(self.info_, ensure_ascii=False)

    def parse_info(self, emby_media_info):
        episode_item = emby_media_info["Item"]
        self.info_["Name"] = episode_item["SeriesName"]
        self.info_["PremiereYear"] = (
            int(episode_item["PremiereDate"])
            if episode_item["PremiereDate"].isdigit()
            else my_utils.iso8601_convert_CST(episode_item["PremiereDate"]).year
        )
        self.info_["ProviderIds"] = episode_item["ProviderIds"]
        self.info_["Series"] = episode_item["IndexNumber"]
        self.info_["Season"] = episode_item["ParentIndexNumber"]
        self.server_name_ = emby_media_info["Server"]["Name"]
        log.logger.debug(self.info_)

    def get_caption(self):
        if "Tmdb" not in self.info_["ProviderIds"]:
            if "Tvdb" not in self.info_["ProviderIds"]:
                tvdb_id, err = tvdb_api.search_series(self.info_["Name"], self.info_["PremiereYear"])
                if err:
                    raise Exception(err)
            else:
                tvdb_id, err = tvdb_api.get_seriesid_by_episodeid(self.info_["ProviderIds"]["Tvdb"])
                if err:
                    raise Exception(err)
            self.info_["ProviderIds"]["Tvdb"] = str(tvdb_id)
            self._get_id()

        tv_details, err = tmdb_api.get_tv_episode_details(
            self.info_["ProviderIds"]["Tmdb"],
            self.info_["Season"],
            self.info_["Series"],
        )
        if err:
            log.logger.error(err)
            raise Exception(err)

        # check server name and escape any special characters
        for ch in self.escape_ch:
            self.server_name_ = self.server_name_.replace(ch, "\\" + ch)
        
        self.caption_ = self.caption_.format(
            server_name=self.server_name_,
            type_ch="剧集",
            title=self.info_["Name"] + " " + tv_details["name"],
            year=tv_details["air_date"][:4],
            episode="已更新至 第{}季 第{}集\n".format(
                tv_details["season_number"], tv_details["episode_number"]
            ),
            rating=tv_details["vote_average"],
            rel=tv_details["air_date"],
            intro=tv_details["overview"],
            type="tv",
            tmdbid=self.info_["ProviderIds"]["Tmdb"],
        )
        log.logger.debug(self.caption_)

    def get_poster(self):
        self.poster_, err = tmdb_api.get_tv_season_poster(
            self.info_["ProviderIds"]["Tmdb"], self.info_["Season"]
        )
        if err:
            log.logger.error(err)
            raise Exception(err)

    def send_caption(self):
        if self.poster_:
            tgbot.send_photo(self.caption_, self.poster_)
        else:
            tgbot.send_message(self.caption_)


def create_media(emby_media_info):
    if emby_media_info["Item"]["Type"] == "Movie":
        return Movie()
    elif emby_media_info["Item"]["Type"] == "Episode":
        return Episode()
    else:
        raise Exception("Unsupported media type.")


def jellyfin_msg_preprocess(msg):
    # jellyfin msg 部分字段中包含 "\n"，不处理会导致 json.loads() 失败
    if '\n' in msg:
        msg = msg.replace('\n', '')
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
            "Server": {"Name": "server name"},
        }
        jellyfin_msg["Server"]["Name"] = original_msg["ServerName"]
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
        # FIXME: Jellyfin 部分剧集没有提供 Provider_imdb 和 Provider_tvdb 信息（目前仅发现国产剧没有 Provider_xx 信息）
        if jellyfin_msg["Item"]["ProviderIds"] == {}:
            log.logger.warning(f"Jellyfin Server not get any ProviderIds for Event: {jellyfin_msg['Title']}")
        return jellyfin_msg
    else:
        return original_msg



def process_media(emby_media_info):
    emby_media_info = jellyfin_msg_preprocess(emby_media_info)
    if not emby_media_info:
        return
    log.logger.info(f"Received message: {emby_media_info['Title']}")
    if emby_media_info["Event"] != "library.new":
        log.logger.warning(f"Unsupported event type: {emby_media_info['Event']}")
        return
    try:
        md = create_media(emby_media_info)
        md.parse_info(emby_media_info)
        md.get_caption()
        md.get_poster()
        md.send_caption()
    except Exception as e:
        raise e
    else:
        log.logger.info(f"Message processing completed: {emby_media_info['Title']}")
