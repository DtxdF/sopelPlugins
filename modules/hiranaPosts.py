import feedparser
from sopel import module

PUBLIC_AREA = "public"
PRIVATE_AREA = "private"
DEFAULT_AREA = PRIVATE_AREA
DEFAULT_INDEX = 0 # 10 máximos
FORMAT = "{ID}.- '{SUBJECT}' por {USERNAME} - {POSTURL}"
MAX_POSTS = 10

@module.commands("hiranaPosts")
@module.example(".hiranaPosts [private|public]")
def hiranaPosts(bot, trigger):
	"""Muestra las diez publicaciones más recientes del blog de Hirana."""

	index = trigger.group(3)
	area = trigger.group(4)

	if (index is None):
		index = DEFAULT_INDEX

	if (area is None):
		area = DEFAULT_AREA

	# Para que el usuario tenga la posibilidad de usar los argumentos
	# como le plazca.
	try:
		index = int(index)
	except ValueError:
		area = index
		index = DEFAULT_INDEX

	if (index > MAX_POSTS):
		bot.say("El índice supera el límite permitido")
		return

	if (area == PUBLIC_AREA):
		destination = None
	elif (area == PRIVATE_AREA):
		destination = trigger.nick
	else:
		bot.say("Por favor, eliga *private* o *public*, y no cualquier otro.")
		return

	f = feedparser.parse("https://hirana.net/feed")["entries"]

	for (nid, post) in enumerate(f, 1):
		if (index > 0 and nid != index):
			continue

		link = post["link"]
		author = post["author"]
		title = post["title"]

		bot.say(FORMAT.format(
			ID=nid,
			SUBJECT=title,
			USERNAME=author,
			POSTURL=link
		), destination)
