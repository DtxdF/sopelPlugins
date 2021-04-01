import requests
from sopel import module

@module.commands("clima")
@module.example(".clima [ubicación]")
def clima(bot, trigger):
	"""
Muestra el clima actual de algún lugar. Vea [http://wttr.in/:help] para
ver más detalles de la ubicación.
	"""

	place = trigger.group(3) or ""
	r = requests.get("http://wttr.in/%s?lang=es&format=3&m" % place)

	bot.say(r.text.strip())
