import json
import requests

"""
https://contextualwebsearch.com/freeapi
"""


def find_images(query, count=1, auto_complete=True):
    return _find_impl(
        "https://contextualwebsearch.com/api/Search/ImageSearchAPI",
        query, count, auto_complete,
    )


def find_web(query, count=1, auto_complete=True):
    return _find_impl(
        "https://contextualwebsearch.com/api/Search/WebSearchAPI",
        query, count, auto_complete,
    )


def find_news(query, count=1, auto_complete=True):
    return _find_impl(
        "https://contextualwebsearch.com/api/Search/NewsSearchAPI",
        query, count, auto_complete,
    )


def _find_impl(url, query, count, auto_complete):
    """Returns list of urls, or error string"""
    try:
        res = requests.get(
            url,
            params={"q": query, "count": count, "autoCorrect": ("true" if auto_complete else "false")},
        )
    except (requests.ConnectionError, requests.ConnectTimeout):
        return "`connection error`"

    try:
        data = json.loads(res.content.decode("utf-8"))
    except ValueError:
        return "`no valid json`"
    #print(data)

    if not data.get("value"):
        return "Nix"

    return [v["url"] for v in data["value"]]
