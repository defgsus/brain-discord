import discord
import random


from tools.messages import *
from tools.pyeval import evaluate_python


def rand_choice(seq):
    return seq[random.randrange(len(seq))]


class BrianBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super(BrianBot, self).__init__(*args, **kwargs)
        self.nonsense = None
        self.nonsense_key = ""
        self.do_annoy = True
        self.do_speak = True

    def get_members(self):
        members = set()
        for serv in self.servers:
            for mem in serv.members:
                if mem != self.user:
                    members.add(mem)
        return list(members)

    def get_member_names(self):
        return [m.display_name for m in self.get_members()]

    def _send(self, channel, text, do_speak=True):
        if not text and not text.strip():
            return []
        msgs = split_text(text)
        for count, msg in enumerate(msgs):
            if len(msg):
                yield from self.send_message(channel, msg, tts=self.do_speak and do_speak)
                if count < len(msgs) - 1:
                    yield from self.send_typing(channel)

    def on_message(self, message):
        print("(%s, %s) %s: %s" % (message.channel.name, message.channel.type,
                                   message.author.display_name, message.content))
        # we do not want the bot to reply to itself
        if message.author == self.user:
            return []

        msgl = message.content.lower()
        channel = message.channel

        response = None

        if msgl.startswith("!py "):
            response = evaluate_python(msgl[4:])

        if not response:
            return []

        yield from self._send(channel, response)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        for m in self.get_members():
            print("%s %s" % (m.display_name.ljust(20), m.id))


if __name__ == "__main__":
    from tools.bot_credentials import BOT_TOKEN

    bot = BrianBot()
    bot.run(BOT_TOKEN)
