## yet another discord bot




### deployment

To create a bot and token see [discordapp](https://discordapp.com/developers/applications/me), 
a walk-through can be found [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).

Create `tools/bot_credentials.py` and insert:
```python
BOT_TOKEN = "your_token"
```

Then,
```bash
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
python brian-bot.py
```
