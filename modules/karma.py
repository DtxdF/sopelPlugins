import json
import re
import time
from sopel import module
from sopel import formatting
from sopel.formatting import colors

KARMA_KEY = "karma"
KARMA_KEY_INFO = "karma_info"
BLOCKLIST_RE = r"^(I|i)nvitado\d+$"
LIMIT_SECOND = 10

@module.commands("karma")
@module.example(".karma <Nombre de usuario> [-/+]")
def karma(bot, trigger):
    """Otorga más karma a un usuario"""

    nick = trigger.group(3)

    if (nick is None):
        bot.reply(formatting.color("¡Sigue la sintaxis!", colors.YELLOW))
        return
    else:
        nick = nick.lower().strip()

    is_sum = trigger.group(4)
    if (is_sum is None or is_sum[:1] == "+"):
        is_sum = True
    elif (is_sum[:1] == "-"):
        is_sum = False
    else:
        bot.reply(formatting.color("No comprendo qué quieres que haga.", colors.YELLOW))
        return

    if (re.match(BLOCKLIST_RE, trigger.nick)):
        bot.reply(formatting.color("¡No voy a permitir que otorgues karma a este usuario!", colors.YELLOW))
        return

    if (re.match(BLOCKLIST_RE, nick)):
        bot.reply(formatting.color("¡No voy a permitir que le des karma!", colors.YELLOW))
        return

    if (nick == trigger.nick.lower()):
        bot.reply(formatting.color("¡No te puedes dar karma a ti mismo!", colors.YELLOW))
        return

    if not (nick in bot.users):
        bot.reply(formatting.color("Este usuario no existe o no se encuentra, intenta otra vez.", colors.RED))
        return

    karma_info = bot.db.get_nick_value(nick, KARMA_KEY_INFO)
    if (karma_info is not None):
        karma_info = json.loads(karma_info)
    else:
        karma_info = {}

    karma_info["start_karma"] = karma_info.get("start_karma")
    if (karma_info["start_karma"] is None):
        karma_info["start_karma"] = time.time()
    elif (round(time.time()-karma_info["start_karma"]) < LIMIT_SECOND):
        bot.reply("Todavía no puedes dar karma, porque todavía no se superan los %ds segundos" % (LIMIT_SECOND))
        return
    else:
        karma_info["start_karma"] = time.time()

    karma_val = bot.db.get_nick_value(nick, KARMA_KEY, 0)
    karma_val = int(karma_val)
    if (is_sum):
        karma_val += 1
    else:
        karma_val -= 1

    bot.db.set_nick_value(nick, KARMA_KEY, karma_val)
    bot.db.set_nick_value(nick, KARMA_KEY_INFO, json.dumps(karma_info))
    bot.say(formatting.color("%s recibe %s1 de karma de parte de %s. Ahora tiene %d." % (
        nick,
        "+" if (is_sum) else "-",
        trigger.nick,
        karma_val
    ), colors.LIGHT_GREEN if (is_sum) else colors.YELLOW))

@module.commands("getKarma")
def getKarma(bot, trigger):
    """Obtiene el karma de un usuario"""

    nick = trigger.group(2) or trigger.nick
    nick = nick.lower().strip()

    karma_val = bot.db.get_nick_value(nick, KARMA_KEY)
    if (karma_val is None):
        bot.reply("%s no existe." % (nick))
        return

    bot.say("%s tiene %d de karma." % (nick, karma_val))
