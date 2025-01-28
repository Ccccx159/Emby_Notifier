#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests, os, log

TMDB_API = "https://api.themoviedb.org/3"

TMDB_API_TOKEN = os.getenv("TMDB_API_TOKEN")
TMDB_IMAGE_DOMAIN = os.getenv("TMDB_IMAGE_DOMAIN", "https://image.tmdb.org")

TMDB_API_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer {}".format(TMDB_API_TOKEN),
}

TMDB_MEDIA_TYPES = {
    "Movie": "movie",
    "Episode": "tv",
}

TMDB_LANG = "zh-CN"


def login():
    """
    Logs in to the TMDB API.

    Returns:
        tuple: A tuple containing a boolean value indicating the success of the login and an error message if login fails.
    """
    login_url = f"{TMDB_API}/authentication"
    try:
        response = requests.get(login_url, headers=TMDB_API_HEADERS, timeout=5)
        response.raise_for_status()
        log.logger.info("TMDB login successful.")
    except requests.exceptions.ConnectionError as e:
        log.logger.error(f"TMDB login failed. Check network connection: {e}")
        raise e
    except requests.exceptions.RequestException as e:
        log.logger.error(f"TMDB login failed. {response.json()['status_message']} Current API token: {TMDB_API_TOKEN}")
        raise e


def search_media(media_type, name, year):
    """
    Search for movies or TV shows on TMDB API.

    Args:
        type (str): The type of media to search for. Valid values are 'Movie' or 'Episode'.
        name (str): The name of the movie or TV show to search for.
        year (int): The year of release for the movie or TV show.

    Returns:
        list: A list of search results as dictionaries.
        str: An error message if the search fails.
    """
    media_type = (
        TMDB_MEDIA_TYPES[media_type] if media_type in TMDB_MEDIA_TYPES else media_type
    )
    search_url = f"{TMDB_API}/search/{media_type}?query={name}&language={TMDB_LANG}&page=1"
    if year != -1:
        search_url += f"&year={year}"
    try:
        response = requests.get(search_url, headers=TMDB_API_HEADERS)
        response.raise_for_status()
        return response.json().get("results", []), None
    except requests.exceptions.RequestException as e:
        return (
            [],
            f"TMDB search for {name} failed. Check network connection or API token: {e}",
        )


def get_external_ids(media_type, tmdb_id):
    """
    Fetches the external IDs for a given media type and TMDB ID.

    Args:
      media_type (str): The type of media (e.g., 'Movie', 'Episode').
      tmdb_id (int): The TMDB ID of the media.

    Returns:
      tuple: A tuple containing the response JSON and an error message (if any).
        - response_json (dict): The JSON response containing the external IDs.
        - error_message (str): An error message if the request fails, otherwise None.
    """
    media_type = (
        TMDB_MEDIA_TYPES[media_type] if media_type in TMDB_MEDIA_TYPES else media_type
    )
    external_ids_url = (
        f"{TMDB_API}/{media_type}/{tmdb_id}/external_ids?language={TMDB_LANG}"
    )
    try:
        response = requests.get(external_ids_url, headers=TMDB_API_HEADERS)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Failed to fetch external ids for TMDB ID {tmdb_id}. Error: {e}"


def get_movie_details(tmdb_id):
    """
    Fetches detailed information about a movie from TMDB.

    Args:
      tmdb_id (int): The TMDB ID of the movie.

    Returns:
      tuple: A tuple containing the response JSON and an error message (if any).
        - response_json (dict): The JSON response containing the movie details.
        - error_message (str): An error message if the request fails, otherwise None.
    """
    movie_details_url = f"{TMDB_API}/movie/{tmdb_id}?language={TMDB_LANG}"
    try:
        response = requests.get(movie_details_url, headers=TMDB_API_HEADERS)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Failed to fetch movie details for TMDB ID {tmdb_id}. Error: {e}"
    

def get_movie_poster(tmdb_id):
    """
    Fetches the poster URL for a movie from TMDB.

    Args:
      tmdb_id (int): The TMDB ID of the movie.

    Returns:
      tuple: A tuple containing the poster URL and an error message (if any).
        - poster_url (str): The URL of the movie poster.
        - error_message (str): An error message if the request fails, otherwise None.
    """
    movie_details, err_info = get_movie_details(tmdb_id)
    if movie_details:
        poster_path = movie_details.get("poster_path")
        if poster_path:
            poster_url = f"{TMDB_IMAGE_DOMAIN}/t/p/w500{poster_path}"
            return poster_url, None
        return None, f"No poster path found for movie {tmdb_id}."
    return None, err_info


def get_tv_season_details(tmdb_id, season_number):
    """
    Fetches detailed information about a specific season of a TV show from TMDB.

    Args:
      tmdb_id (int): The TMDB ID of the TV show.
      season_number (int): The season number.

    Returns:
      tuple: A tuple containing the response JSON and an error message (if any).
        - response_json (dict): The JSON response containing the season details.
        - error_message (str): An error message if the request fails, otherwise None.
    """
    tv_season_url = (
        f"{TMDB_API}/tv/{tmdb_id}/season/{season_number}?language={TMDB_LANG}"
    )
    try:
        response = requests.get(tv_season_url, headers=TMDB_API_HEADERS)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return (
            None,
            f"Failed to fetch TV season details for season {season_number}. Error: {e}",
        )


def get_tv_season_poster(tmdb_id, season_number):
    """
    Fetches the poster URL for a specific season of a TV show from TMDB.

    Args:
      tmdb_id (int): The TMDB ID of the TV show.
      season_number (int): The season number.

    Returns:
      tuple: A tuple containing the poster URL and an error message (if any).
        - poster_url (str): The URL of the season poster.
        - error_message (str): An error message if the request fails, otherwise None.
    """
    season_details, err_info = get_tv_season_details(tmdb_id, season_number)
    if season_details:
        poster_path = season_details.get("poster_path")
        if poster_path:
            poster_url = f"{TMDB_IMAGE_DOMAIN}/t/p/w500{poster_path}"
            return poster_url, None
        return None, "No poster path found for TV {tmdb_id} season {season_number}."
    return None, err_info


def get_tv_episode_details(tmdb_id, season_number, episode_number):
    """
    Fetches detailed information about a specific episode of a TV show from TMDB.

    Args:
      tmdb_id (int): The TMDB ID of the TV show.
      season_number (int): The season number of the episode.
      episode_number (int): The episode number within the season.

    Returns:
      tuple: A tuple containing the response JSON and an error message (if any).
        - response_json (dict): The JSON response containing the episode details.
        - error_message (str): An error message if the request fails, otherwise None.
    """
    tv_episode_url = f"{TMDB_API}/tv/{tmdb_id}/season/{season_number}/episode/{episode_number}?language={TMDB_LANG}"
    try:
        response = requests.get(tv_episode_url, headers=TMDB_API_HEADERS)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return (
            None,
            f"Failed to fetch TV episode details for S{season_number}E{episode_number}. Error: {e}",
        )


def get_movie_backdrop_path(tmdb_id):
    """
    Get the backdrop path for a movie based on its TMDB ID.

    Args:
        tmdb_id (int): The TMDB ID of the movie.

    Returns:
        tuple: A tuple containing the backdrop path (str) and an error message (str).
               If the backdrop path is found, the error message will be None.
               If the backdrop path is not found, the backdrop path will be None and the error message will contain the movie ID.
    """
    movie_details, err_info = get_movie_details(tmdb_id)
    if movie_details:
        backdrop_path = movie_details.get("backdrop_path")
        if backdrop_path:
            return f"{TMDB_IMAGE_DOMAIN}/t/p/w500{backdrop_path}", None
        return None, f"No backdrop path found for movie {tmdb_id}."
    return None, err_info


def get_tv_episode_still_paths(tmdb_id, season_number, episode_number):
    episode_details, err = get_tv_episode_details(tmdb_id, season_number, episode_number)
    if episode_details:
        still = episode_details.get("still_path")
        if still:
            return f"{TMDB_IMAGE_DOMAIN}/t/p/w500{still}", None
        return None, f"No stills found for TV {tmdb_id} S{season_number}E{episode_number}."