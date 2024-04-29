#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import abc
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
            "#影视更新\n"
            + "\[{type_ch}]\n"
            + "片名： *{title}* ({year})\n"
            + "{episode}"
            + "评分： {rating}\n\n"
            + "上映日期： {rel}\n\n"
            + "内容简介： {intro}\n\n"
            + "相关链接： [TMDB](https://www.themoviedb.org/{type}/{tmdbid}?language=zh-CN)\n"
        )
        self.poster_ = ""

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


class Movie(IMedia):
    def __init__(self):
        super().__init__()
        self.info_["Type"] = "Movie"
    
    def __str__(self) -> str:
        return self.info_

    def parse_info(self, emby_media_info):
        movie_item = emby_media_info["Item"]
        self.info_["Name"] = movie_item["Name"]
        self.info_["PremiereYear"] = my_utils.iso8601_convert_CST(
            movie_item["PremiereDate"]
        ).year
        self.info_["ProviderIds"] = movie_item["ProviderIds"]
        log.logger.debug(self.info_)

    def get_caption(self):
        if "Tmdb" not in self.info_["ProviderIds"]:
            movies, err = tmdb_api.search_media(
                self.info_["Type"], self.info_["Name"], self.info_["PremiereYear"]
            )
            if err:
                raise Exception(err)
            for mov in movies:
                Imdb_id = self.info_["ProviderIds"].get("Imdb", "-1")
                Tvdb_id = self.info_["ProviderIds"].get("Tvdb", "-1")
                ext_ids, err = tmdb_api.get_external_ids(self.info_["Type"], mov["id"])
                if err:
                    log.logger.warning(err)
                    continue
                if Imdb_id == ext_ids.get("imdb_id") or Tvdb_id == str(ext_ids.get("tvdb_id")):
                    self.info_["ProviderIds"]["Tmdb"] = str(mov["id"])
                    break
            if "Tmdb" not in self.info_["ProviderIds"]:
                raise Exception("No matching movie found on TMDB.")
        movie_details, err = tmdb_api.get_movie_details(self.info_["ProviderIds"]["Tmdb"])
        if err:
            raise Exception(err)
        self.caption_ = self.caption_.format(
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
            raise Exception(err)

    def send_caption(self):
        tgbot.send_photo(self.caption_, self.poster_)


class Episode(IMedia):
    def __init__(self):
        super().__init__()
        self.info_["Type"] = "Episode"

    def __str__(self) -> str:
        return self.info_

    def parse_info(self, emby_media_info):
        episode_item = emby_media_info["Item"]
        self.info_["Name"] = episode_item["SeriesName"]
        self.info_["PremiereYear"] = my_utils.iso8601_convert_CST(episode_item["PremiereDate"]).year
        self.info_["ProviderIds"] = episode_item["ProviderIds"]
        self.info_["Series"] = episode_item["IndexNumber"]
        self.info_["Season"] = episode_item["ParentIndexNumber"]
        log.logger.debug(self.info_)

    def get_caption(self):
        if "Tmdb" not in self.info_["ProviderIds"]:
            tvdb_id, err = tvdb_api.get_seriesid_by_episodeid(self.info_["ProviderIds"]["Tvdb"])
            if err:
                raise Exception(err)
            log.logger.debug(tvdb_id)
            series, err = tmdb_api.search_media(self.info_["Type"], self.info_["Name"], self.info_["PremiereYear"])
            if err:
                raise Exception(err)
            for ser in series:
                log.logger.debug(ser)
                ext_ids, err = tmdb_api.get_external_ids(self.info_["Type"], ser["id"])
                if err:
                    log.logger.warning(err)
                    continue
                if tvdb_id == ext_ids.get("tvdb_id"):
                    self.info_["ProviderIds"]["Tmdb"] = str(ser["id"])
                    break
            if "Tmdb" not in self.info_["ProviderIds"]:
                raise Exception("No matching series found on TMDB.")
        tv_details, err = tmdb_api.get_tv_episode_details(self.info_["ProviderIds"]["Tmdb"], self.info_["Season"], self.info_["Series"])
        if err:
            raise Exception(err)
        self.caption_ = self.caption_.format(
            type_ch="剧集",
            title=self.info_["Name"] + " " + tv_details["name"],
            year=tv_details["air_date"][:4],
            episode="已更新至 第{}季 第{}集\n".format(tv_details["season_number"], tv_details["episode_number"]),
            rating=tv_details["vote_average"],
            rel=tv_details["air_date"],
            intro=tv_details["overview"],
            type="tv",
            tmdbid=self.info_["ProviderIds"]["Tmdb"],
        )
        log.logger.debug(self.caption_)
            

    def get_poster(self):
        self.poster_, err = tmdb_api.get_tv_season_poster(self.info_["ProviderIds"]["Tmdb"], self.info_["Season"])
        if err:
            raise Exception(err)

    def send_caption(self):
        if self.poster_:
            tgbot.send_photo(self.caption_, self.poster_)
        else:
            tgbot.send_message(self.caption_)
