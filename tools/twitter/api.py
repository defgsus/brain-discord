import time

from twython import Twython, TwythonStreamer, TwythonError

class TwitterClient:
    def __init__(self, twitter=None):
        from .credentials import TWITTER_APP_KEY, TWITTER_ACCESS_TOKEN
        self.twitter = twitter or Twython(TWITTER_APP_KEY, access_token=TWITTER_ACCESS_TOKEN)

    def search(self, q, count=10, tweet_mode="extended", result_type="mixed", **params):
        """
        https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html
        """
        parms = dict(q=q, count=min(count, 100), tweet_mode=tweet_mode, result_type=result_type, include_entities=1)
        parms.update(params)
        ret = list()
        while True:
            res = self.twitter.search(**parms)
            for tweet in res["statuses"]:
                ret.append(tweet)
            if "search_metadata" not in res:
                break
            if len(ret) >= count:
                break
            next = res["search_metadata"].get("next_results")

            if not next or len(next) < 10:
                break
            max_id = next.split("max_id=")[-1].split("&")[0]
            if not max_id:
                break
            parms["max_id"] = max_id
        return ret

    def get_tweet(self, id):
        return self.twitter.show_status(id=id, tweet_mode="extended")

    def get_user(self, id):
        try:
            return self.twitter.show_user(user_id=id)
        except TwythonError as e:
            print(e)
            return None

    def get_user_tweets(self, user_id):
        kwargs = dict(include_rts=True, user_id=user_id, count=200, trim_user=True, tweet_mode="extended")
        ret = []
        while True:
            start_time = time.time()
            timeline = self.twitter.get_user_timeline(**kwargs)
            if not timeline:
                return ret
            for tweet in timeline:
                ret.append(tweet)
            print("user %s: tweets %s" % (user_id, len(ret)))
            kwargs["max_id"] = timeline[-1]["id"] - 1
            took = time.time() - start_time
            time.sleep(max(0., 1.01 - took))  # limit to one per second

