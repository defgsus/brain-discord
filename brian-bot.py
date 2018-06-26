import random
import time
import discord

from tools.messages import *
from tools.pyeval import evaluate_python
from tools.nonsense import NONSENSE_GENERATORS
from tools import wiki, eliza, twitter, duckduckgo


NERV_PROB = .1  # probability of annoyance in group channels
NAME_LINE_PROB = .7  # probability of using movie citations with names


def rand_choice(seq):
    return seq[random.randrange(len(seq))]


class ChannelConfig:
    def __init__(self):
        self.nonsense = None
        self.nonsense_key = ""
        self.be_quite = False
        self.be_eliza = False


class BrianBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super(BrianBot, self).__init__(*args, **kwargs)
        self.channel_config = dict()
        self.twitter = None

    def get_members(self):
        members = set()
        for serv in self.servers:
            for mem in serv.members:
                if mem != self.user:
                    members.add(mem)
        return list(members)

    def get_member_names(self):
        return [m.display_name for m in self.get_members()]

    def set_nonsense(self, channel, nonsense_key):
        config = self.channel_config[channel]
        if config.nonsense_key == nonsense_key:
            return []
        nonsense = NONSENSE_GENERATORS[nonsense_key]
        print("switching %s nonsense generator to %s" % (channel, nonsense.name))
        config.nonsense = nonsense
        config.nonsense_key = nonsense_key
        # Discord doesn't like switching the username too often!!
        # Also, changing the avatar or name seems to work only occasionally...
        #yield from self.edit_profile(username=config.nonsense.name)#,
        #                             avatar=nonsense.avatar)
        return []

    def _send(self, channel, text):
        if not text and not text.strip():
            return []
        msgs = split_text(text)
        for count, msg in enumerate(msgs):
            if len(msg):
                yield from self.send_message(channel, msg)
                if count < len(msgs) - 1:
                    yield from self.send_typing(channel)
        return []

    def _send_embed(self, channel, text):
        em = discord.Embed(title='My Embed Title', description=text, colour=0xDEADBF)
        em.set_author(name='Someone', icon_url=self.user.default_avatar_url)
        yield from self.send_message(channel, embed=em)

    def on_message(self, message):
        print("(%s, %s) %s: %s" % (message.channel.name, message.channel.type,
                                   message.author.display_name, message.content))
        # we do not want the bot to reply to itself
        if message.author == self.user:
            return []

        msg = message.content.strip("` ")
        msgl = msg.lower()
        channel = message.channel

        if channel not in self.channel_config:
            self.channel_config[channel] = ChannelConfig()
        config = self.channel_config[channel]

        if config.nonsense is None:
            yield from self.set_nonsense(channel, "brian")

    # --- commands ---

        response = None

        if msgl.startswith("!py"):
            yield from self.send_typing(channel)
            response = evaluate_python(msg[3:].strip("` "))
            if not response:
                response = "Nix"
            if "*" in response:
                response = "`%s`" % response

        if msgl.startswith("!wiki"):
            yield from self.send_typing(channel)
            response = self.get_wiki_results(msg[5:].strip("` "))

        if msgl.startswith("!tw"):
            yield from self.send_typing(channel)
            response = self.get_twitter_results(msg[msg.find(" "):].strip("` "))

        if msgl.startswith("!duck") or msgl.startswith("!dd"):
            response = duckduckgo.duckduckgo(msg[msg.find(" "):].strip("` "))

        if response:
            if isinstance(response, (tuple, list)):
                for r in response:
                    yield from self._send(channel, r)
            else:
                yield from self._send(channel, response)
            return []

        # --- random stuff ---

        nerv_prob = 1. if str(message.channel.type) == "private" else NERV_PROB

        # is bot called by name?
        is_mentioned = self.user.name.lower() in msgl or "botti" in msgl or "eliza" in msgl
        if "eliza" in msgl:
            config.be_eliza = True
            config.nonsense_key = "eliza"
        else:
            for x in NONSENSE_GENERATORS:
                if x in msgl or NONSENSE_GENERATORS[x].name in msgl:
                    is_mentioned = True
                    config.be_eliza = False
                    yield from self.set_nonsense(channel, x)
                    break

        if is_mentioned:
            if "schweig" in msgl or "shut up" in msgl or "schnauze" in msgl or "klappe" in msgl:
                config.be_quite = True
            else:
                config.be_quite = False

        if not config.be_quite and (is_mentioned or random.uniform(0, 1) <= nerv_prob or config.be_eliza):
            yield from self.send_typing(channel)
            time.sleep(random.uniform(.5, 2))
            if config.be_eliza:
                yield from self._send(channel, eliza.analyze(msg))
            else:
                yield from self._send(channel,
                                      config.nonsense.rand(0, self.get_member_names(),
                                                           random.uniform(0, 1) <= NAME_LINE_PROB))
        return []

    def get_wiki_results(self, term):
        cc = None
        limit = None
        terms = term.split(" ")
        while len(terms) > 1:
            if terms[0].isdigit() and limit is None:
                limit = min(100, int(terms[0]))
                terms = terms[1:]
            elif len(terms[0]) == 2 and terms[0].isalpha() and cc is None:
                cc = terms[0]
                terms = terms[1:]
            else:
                break

        term = " ".join(terms)
        cc = cc or "de"
        limit = limit or 1

        try:
            results = wiki.opensearch(term, cc=cc, limit=limit)
            if not results:
                response = "Habe diesen Löffel gefunden, Herr!"
            else:
                response = [r["url"] for r in results]
        except BaseException as e:
            response = "`%s`" % e
        return response

    def get_twitter_results(self, query):
        count = 1
        terms = query.split(" ")
        if len(terms) > 1 and terms[0].isdigit():
            count = min(100, int(terms[0]))
            terms = terms[1:]
            query = " ".join(terms)

        if self.twitter is None:
            self.twitter = twitter.TwitterClient()

        tweets = self.twitter.search(query, count=count)

        if not tweets:
            return "Nix"
        return [twitter.tweet_to_discord(t) for t in tweets]

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('---server members---')
        for m in self.get_members():
            print("%s %s" % (m.display_name.ljust(20), m.id))


if __name__ == "__main__":
    from tools.bot_credentials import BOT_TOKEN

    bot = BrianBot()
    bot.run(BOT_TOKEN)

