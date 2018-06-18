import json
import requests


def opensearch(term, limit=10, cc="de"):
    url = "https://%s.wikipedia.org/w/api.php" % cc
    res = requests.get(
        url,
        headers={"User-Agent": "s.berke@netzkolchose.de"},
        params={
            "action": "opensearch",
            "format": "json",
            "limit": limit,
            "search": term,
        }
    )
    data = json.loads(res.content.decode("utf-8"))
    return [{
        "name": data[1][i],
        "desc": data[2][i],
        "url": data[3][i],
    } for i in range(len(data[1]))]


if __name__ == "__main__":

    results = opensearch("Bot")
    for res in results:
        print('%(name)s <a href="%(url)s">wiki</a>\n%(desc)s' % res)
