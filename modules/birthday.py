import datetime
import json
from sopel import module

DATE_FORMAT = "%m-%d"
INTERVAL = 5

@module.commands("birthday")
@module.example(".birthday <MM-DD>")
def birthday(bot, trigger):
	"""Fija tu fecha de cumpleaños."""

	nick = trigger.nick
	birthday = trigger.group(3)
	cdate = datetime.date.today()
	users = bot.db.get_plugin_value("birthday", "users", {})

	if (users != {}):
		users = json.loads(users)

	if (birthday is None):
		bot.say("Debe definir la fecha de cumpleaños.")
		return

	try:
		bd_struct = datetime.datetime.strptime(birthday, DATE_FORMAT)
	except ValueError:
		bot.say("La sintaxis de la fecha de cumpleaños no es correcta.")
		return
	else:
		bd_struct = bd_struct.replace(year=cdate.year)
		bd_struct = datetime.date(
			year=bd_struct.year,
			month=bd_struct.month,
			day=bd_struct.day
		)

	if (cdate > bd_struct):
		bd_struct = bd_struct.replace(year=cdate.year+1)

	users[nick] = bd_struct.ctime()
	bot.db.set_plugin_value("birthday", "users", json.dumps(users))
	bot.say("Avisaré cuando cumplas años :D")

@module.interval(INTERVAL)
def birthday_notice(bot):
	channels = bot.channels.keys()
	users = bot.db.get_plugin_value("birthday", "users", {})
	cdate = datetime.date.today()

	if (users != {}):
		users = json.loads(users)

	for user, birthday in users.copy().items():
		birthday = datetime.datetime.strptime(birthday, "%a %b %d %H:%M:%S %Y")
		birthday = datetime.date(
			year=birthday.year,
			month=birthday.month,
			day=birthday.day
		)
		for channel in channels:
			if (cdate >= birthday):
				bot.say("¡Hoy es el cumpleaños de %s!" % (user), channel)
				birthday = birthday.replace(year=birthday.year+1)
				users[user] = birthday.ctime()
	
	bot.db.set_plugin_value("birthday", "users", json.dumps(users))
