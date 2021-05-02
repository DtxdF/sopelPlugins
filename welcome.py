import random
import logging
from sopel import module

WELCOME_MESSAGES = "/home/virgilio/.local/etc/virgilio/welcome_messages"

with open(WELCOME_MESSAGES) as fd:
    messages = fd.readlines()

@module.event("JOIN")
@module.unblockable
def welcome(bot, trigger):
    nick_bot = bot.config.get("core", "nick")
    
    if (trigger.nick == nick_bot):
        return

    index = random.randint(0, len(messages)-1)
    message = messages[index]
    message = message.strip()

    bot.say(message % (trigger.nick))
