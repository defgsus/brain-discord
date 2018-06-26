import requests
import json
import bs4


def duckduckgo(query):
    try:
        res = requests.get(
            "https://api.duckduckgo.com",
            params={"format": "json", "q": query},
            timeout=1,
        )
    except (requests.ConnectionError, requests.ConnectTimeout):
        return "`connection error`"

    try:
        data = json.loads(res.content.decode("utf-8"))
    except ValueError:
        return "`no valid json`"
    #print(data)

    return "**%s**\n%s\n%s" % (
        data.get("Heading"),
        bs4.BeautifulSoup(data.get("AbstractText")).text,
        data.get("AbstractURL"),
    )


if __name__ == "__main__":
    print(duckduckgo("django modeladmin"))
