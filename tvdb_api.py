#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests, os
import log

TVDB_API = "https://api4.thetvdb.com/v4"

TVDB_API_KEY = os.getenv("TVDB_API_KEY")

TVDB_API_TOKEN = ""

TVDB_API_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer {TVDB_API_TOKEN}"
}


def login():
    """
    Log in to the TVDB API and get an access token.

    Returns:
        str: The access token.
        str: An error message if the login fails.
    """
    login_url = f"{TVDB_API}/login"
    login_data = {"apikey": TVDB_API_KEY}
    try:
        response = requests.post(login_url, json=login_data, headers=TVDB_API_HEADERS)
        response.raise_for_status()
        global TVDB_API_TOKEN
        TVDB_API_TOKEN = response.json().get("data", {}).get("token", "")
        log.logger.debug(response.json())
        TVDB_API_HEADERS["Authorization"] = f"Bearer {TVDB_API_TOKEN}"
        return TVDB_API_TOKEN, None
    except requests.exceptions.RequestException as e:
        return None, f"TVDB login failed. Check network connection or API key: {e}"


def get_seriesid_by_episodeid(episode_id):
    """
    Get the series ID for a given episode ID.

    Args:
        episode_id (int): The TVDB episode ID.

    Returns:
        int: The TVDB series ID.
        str: An error message if the request fails.
    """
    global TVDB_API_TOKEN
    for _ in range(2):
        if TVDB_API_TOKEN == "":
            TVDB_API_TOKEN, err = login()
            if err:
                return None, err
        episode_url = f"{TVDB_API}/episodes/{episode_id}"
        try:
            response = requests.get(episode_url, headers=TVDB_API_HEADERS)
            response.raise_for_status()
            return response.json().get("data", {}).get("seriesId"), None
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 401:
                TVDB_API_TOKEN = ""
                continue
            else:
                break
    return None, f"TVDB episode ID {episode_id} not found: {e}"
        
    