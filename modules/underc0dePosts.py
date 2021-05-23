import urllib.parse
import requests
from bs4 import BeautifulSoup
from sopel import module

PUBLIC_AREA = "public"
PRIVATE_AREA = "private"
DEFAULT_AREA = PRIVATE_AREA
DEFAULT_INDEX = 0 # 10 máximos
FORMAT = "{ID}.- '{SUBJECT}' por {USERNAME} - {POSTURL}"
MAX_POSTS = 10

@module.commands("underc0dePosts")
@module.example(".underc0dePosts [index] [public|private]")
def underc0dePosts(bot, trigger):
	"""Obtiene las últimas diez publicaciones del foro underc0de.org"""

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

	r = requests.get("https://underc0de.org/foro/index.php?action=recent")
	soup = BeautifulSoup(r.text, "lxml")

	for (nid, post) in enumerate(soup.find_all(class_="topic_details"), 1):
		if (index > 0 and nid != index):
			continue

		url = post.find_all("a")
		postObj = url[1]
		postURL = deleteSESSID(postObj["href"])
		profile = url[2]
		profileName = profile.string
		profileURL = deleteSESSID(profile["href"])
		subject = postObj.string

		bot.say(FORMAT.format(
			ID=nid,
			SUBJECT=subject,
			USERNAME=profileName,
			POSTURL=postURL
		), destination)

def deleteSESSID(url):
	url_split = urllib.parse.urlsplit(url)
	url_split = url_split._replace(query="")

	return urllib.parse.urlunsplit(url_split)
