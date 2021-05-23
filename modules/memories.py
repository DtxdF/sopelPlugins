import logging
import os
import re
import shlex
from sopel import module

FORMAT = "{ID}.- {KEY} - {VALUE}"
BLOCKLIST_WORDS = (
	"seen_action",
	"seen_channel",
	"seen_message",
	"seen_timestamp"
)
BLOCKLIST_RE = "|".join(BLOCKLIST_WORDS)
BLOCKLIST_RE = "(%s)" % (BLOCKLIST_RE)

@module.commands("memories")
@module.example(".memories <Nombre del recuerdo> [Valor del recuerdo]")
def memories(bot, trigger):
	"""Obtener o crear un recuerdo."""

	nick = trigger.nick
	args = shlex.split(trigger.group(2))[:2]

	if (args == []):
		bot.say("Por favor, siga la sintaxis.")
		return

	value = None
	if (len(args) == 2):
		(name, value) = args
	else:
		(name,) = args

	if (re.match(BLOCKLIST_RE, name)):
		bot.say("No se permite este nombre.")
		return

	if (value is None):
		value = bot.db.get_nick_value(nick, name)

		if (value is None):
			bot.say("El nombre '%s' no existe en tus recuerdos." % (name))
		else:
			bot.say(value)
	else:
		bot.db.set_nick_value(nick, name, value)
		bot.say("Ahora podrás recordar a '%s'" % (name))

@module.commands("delMemories")
@module.example(".delMemories <Nombre del recuerdo>")
def delMemories(bot, trigger):
	"""Borra un recuerdo de tu memoria."""

	nick = trigger.nick
	name = trigger.group(2)

	if (re.match(BLOCKLIST_RE, name)):
		boy.say("No se permite este nombre.")
		return

	value = bot.db.get_nick_value(nick, name)
	if (value is None):
		bot.say("El recuerdo '%s' no existe." % (name))
		return

	bot.db.delete_nick_value(nick, name)
	bot.say("El recuerdo '%s' se ha borrado." % (name))

@module.commands("searchMemories")
@module.example(".searchMemories <Patrón>")
def searchMemories(bot, trigger):
    """Encontrar recuerdos con una búsqueda (analiza tanto el nombre del recuerdo, como el valor)."""

    name2search = trigger.group(2)
    
    if (name2search is None) or not (name2search.strip()):
        bot.reply("Por favor, escribe una búsqueda.")
        return

    nick = trigger.nick
    nick_id = bot.db.get_nick_id(nick)
    query = "SELECT key, value FROM nick_values WHERE nick_id = ?"
    result = bot.db.execute(query, (nick_id,))

    id = 0
    for (name, value) in result:
        if (re.match(BLOCKLIST_RE, name)):
            continue

        try:
            rex = (re.search(name2search, name)) or (re.search(name2search, value))
        except Exception as err:
            bot.say("Expresión regular inválida: %s." % err)
            logging.exception("Error en una expresión regular")
            return

        if (rex):
            id += 1
            fmt = FORMAT.format(
                ID=id,
                KEY=name,
                VALUE=value
            )
            bot.say(fmt)

    if (id == 0):
        bot.reply("Lo siento, pero no tienes recuerdos.")
