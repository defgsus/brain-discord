import datetime

from .api import TwitterClient


def tweet_to_discord(tweet):
    screen_name = "-"
    if "user" in tweet:
        screen_name = tweet["user"].get("screen_name", "-")
    url = "https://twitter.com/%s/status/%s" % (screen_name, tweet.get("id"))

    try:
        date = datetime.datetime.strptime(tweet.get("created_at"),
                                          "%a %b %d %H:%M:%S %z %Y")
        response = "%s (%s)" % (url, date.strftime("%Y-%m-%d %H:%M:%S"))
    except ValueError:
        response = url

    return response


def tweet_to_discord_extended(tweet):

    text = None
    if "extended_tweet" in tweet:
        text = tweet["extended_tweet"].get("full_text")
    if not text:
        text = tweet.get("full_text") or tweet.get("text")

    try:
        date = datetime.datetime.strptime(tweet.get("created_at"),
                                          "%a %b %d %H:%M:%S %z %Y")
    except ValueError:
        date = None

    user = None
    if "user" in tweet:
        user = tweet["user"].get("name")
        user2 = tweet["user"].get("screen_name")
        if user2 != user:
            user = "%s (@%s)" % (user, user2)

    url = "https://twitter.com/-/status/%s" % tweet.get("id")

    resp = "%s\n" % date if date else ""
    if user:
        resp += "%s\n" % user
    if url:
        resp += "%s\n" % url
    resp += "```\n%s```" % text
    return resp
