import os
import re
import shlex
from sopel import formatting
from sopel import module
from sopel.formatting import colors

FORMAT = "{ID}.- {KEY} - {VALUE}"
BLOCKLIST_WORDS = (
	"seen_action",
	"seen_channel",
	"seen_message",
	"seen_timestamp"
)
BLOCKLIST_RE = repr("|".join(BLOCKLIST_WORDS))

@module.commands("memories")
@module.example(".memories <Nombre del recuerdo> [Valor del recuerdo]")
def memories(bot, trigger):
	"""Obtener o crear un recuerdo."""

	nick = trigger.nick
	args = shlex.split(trigger.group(2))[:2]

	if (args == []):
		bot.say(formatting.color("Por favor, siga la sintaxis.", colors.YELLOW))
		return

	value = None
	if (len(args) == 2):
		(name, value) = args
	else:
		(name,) = args

	if (re.match(BLOCKLIST_RE, name)):
		boy.say(formatting.color("No se permite este nombre.", colors.YELLOW))
		return

	if (value is None):
		value = bot.db.get_nick_value(nick, name)

		if (value is None):
			bot.say(formatting.color("El nombre '%s' no existe en tus recuerdos." % (name), colors.YELLOW))
		else:
			bot.say(value)
	else:
		bot.db.set_nick_value(nick, name, value)
		bot.say(formatting.color("Ahora podrás recordar a '%s'" % (name), colors.GREEN))

@module.commands("delMemories")
@module.example(".delMemories <Nombre del recuerdo>")
def delMemories(bot, trigger):
	"""Borra un recuerdo de tu memoria."""

	nick = trigger.nick
	name = trigger.group(2)

	if (re.match(BLOCKLIST_RE, name)):
		boy.say(formatting.color("No se permite este nombre.", colors.YELLOW))
		return

	value = bot.db.get_nick_value(nick, name)
	if (value is None):
		bot.say(formatting.color("El recuerdo '%s' no existe." % (name), colors.YELLOW))
		return

	bot.db.delete_nick_value(nick, name)
	bot.say(formatting.color("El recuerdo '%s' se ha borrado." % (name), colors.YELLOW))

@module.commands("searchMemories")
@module.example(".searchMemories <Patrón>")
def searchMemories(bot, trigger):
	"""Encontrar recuerdos con una búsqueda (analiza tanto el nombre del recuerdo, como el valor)."""

	name2search = trigger.group(2)
	nick = trigger.nick
	nick_id = bot.db.get_nick_id(nick)
	query = "SELECT key, value FROM nick_values WHERE nick_id = ?"
	result = bot.db.execute(query, (nick_id,))

	id = 1
	for (name, value) in result:
		if (re.match(BLOCKLIST_RE, name)):
			continue

		exp = "^%s(.*)$" % re.escape(name2search)
		if (re.match(exp, name)) or (re.search(exp, value)):
			fmt = FORMAT.format(
				ID=id,
				KEY=name,
				VALUE=value
			)
			bot.say(fmt)
			id += 1
