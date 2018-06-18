import random
import time
import discord

from tools.messages import *
from tools.pyeval import evaluate_python
from tools.nonsense import NONSENSE_GENERATORS
from tools import wiki


NERV_PROB = .1  # probability of annoyance in group channels
NAME_LINE_PROB = .7  # probability of using movie citations with names


def rand_choice(seq):
    return seq[random.randrange(len(seq))]


class BrianBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super(BrianBot, self).__init__(*args, **kwargs)
        self.nonsense = None
        self.nonsense_key = ""
        # set of channels
        self.be_quite = set()

    def get_members(self):
        members = set()
        for serv in self.servers:
            for mem in serv.members:
                if mem != self.user:
                    members.add(mem)
        return list(members)

    def get_member_names(self):
        return [m.display_name for m in self.get_members()]

    def set_nonsense(self, nonsense_key):
        if self.nonsense_key == nonsense_key:
            return []
        nonsense = NONSENSE_GENERATORS[nonsense_key]
        print("switching nonsense generator to %s" % nonsense.name)
        self.nonsense = nonsense
        self.nonsense_key = nonsense_key
        # Discord doesn't like switching the username too often!!
        # Also, changing the avatar or name seems to work only occasionally...
        #yield from self.edit_profile(username=self.nonsense.name,
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

        if self.nonsense is None:
            yield from self.set_nonsense("brian")

        msg = message.content.strip("` ")
        msgl = msg.lower()
        channel = message.channel

        # --- commands ---

        response = None

        if msgl.startswith("!py"):
            yield from self.send_typing(channel)
            response = evaluate_python(msg[3:].strip("` "))
            if "*" in response:
                response = "`%s`" % response

        if msgl.startswith("!wiki"):
            yield from self.send_typing(channel)
            response = self.get_wiki_results(msg[5:].strip("` "))

        if response:
            yield from self._send(channel, response)
            return []

        # --- random stuff ---

        nerv_prob = 1. if str(message.channel.type) == "private" else NERV_PROB

        # is bot called by name?
        is_mentioned = self.user.name.lower() in msgl or "botti" in msgl
        for x in NONSENSE_GENERATORS:
            if x in msgl or NONSENSE_GENERATORS[x].name in msgl:
                is_mentioned = True
                yield from self.set_nonsense(x)
                break

        if is_mentioned:
            if "schweig" in msgl or "shut up" in msgl or "schnauze" in msgl or "klappe" in msgl:
                self.be_quite.add(channel)
            else:
                if channel in self.be_quite:
                    self.be_quite.remove(channel)

        if channel not in self.be_quite and (is_mentioned or random.uniform(0, 1) <= nerv_prob):
            yield from self.send_typing(channel)
            time.sleep(random.uniform(.5, 2))
            yield from self._send(channel, self.nonsense.rand(0, self.get_member_names(),
                                                              random.uniform(0, 1) <= NAME_LINE_PROB))
        return []

    def get_wiki_results(self, term):
        cc = None
        limit = None
        terms = term.split(" ")
        while len(terms) > 1:
            if terms[0].isdigit() and limit is None:
                limit = int(terms[0])
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
                response = "\n".join(r["url"] for r in results)
        except BaseException as e:
            response = "`%s`" % e
        return response

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
