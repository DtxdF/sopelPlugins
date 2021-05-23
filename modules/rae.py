import json
import os
import re
import requests
from bs4 import BeautifulSoup
from sopel import module

RAE_URL = "https://dle.rae.es"
URL = "%s/{word}?m=form" % (RAE_URL)
# Ámbitos
PRIVATE_AREA = "private"
PUBLIC_AREA = "public"
DEFAULT_AREA = PRIVATE_AREA

@module.commands("rae")
@module.example(".rae <Palabra> [public|private]")
def rae_get(bot, trigger):
	"""Muestra las acepciones de una palabra desde dle.rae.es"""

	word = trigger.group(3)
	area = trigger.group(4) or DEFAULT_AREA
	if (area == PUBLIC_AREA):
		destination = None
	elif (area == PRIVATE_AREA):
		destination = trigger.nick
	else:
		bot.say("Por favor, eliga *private* o *public*, y no cualquier otro.")
		return

	if (word is None):
		bot.say("Por favor, escriba la palabra a buscar.", destination)
		return

	db_word = bot.db.get_plugin_value("rae", word)

	if (db_word is not None):
		words = json.loads(db_word)
		for (nid, meanings) in enumerate(words, 1):
			bot.say("%s#%d:" % (word, nid), destination)
			for meaning in meanings:
				bot.say("  %s" % meaning, destination)
	else:
		r = requests.get(URL.format(
			word=word
		))
		soup = BeautifulSoup(r.text, "lxml")
		alphabet_soup = soup.find(id="resultados")

		# Significa que hay una ambigüedad
		vease_title = alphabet_soup.find(title="Véase")
		if (vease_title is not None and vease_title != []):
			new_url = "%s/%s" % (
				RAE_URL,
				vease_title.next_sibling.next_sibling["href"]
			)
			r = requests.get(new_url)
			soup = BeautifulSoup(r.text, "lxml")
			alphabet_soup = soup.find(id="resultados")

		# Si no tiene atributos la etiqueta span, entonces la palabra no existe.
		if (alphabet_soup.span is None):
			bot.say("La palabra %s no está en el Diccionario." % (word), destination)
			return

		if (alphabet_soup.span.attrs == {}):
			bot.say("".join(list(alphabet_soup.span.strings)), destination)
			return

		words = []
		nid = 0
		# Es necesario obtener el identificador, para obtener las palabras
		for article in alphabet_soup("article", id=True):
			if (article.next_element != "\n"):
				continue
			else:
				nid += 1
			bot.say("%s#%d:" % (word, nid), destination)
			meanings = article.find_all(class_=re.compile(r"j\d*"))
			# Para guardarlo en la base de datos
			meanings2storage = []
			for meaning in meanings:
				meaning = "".join(list(meaning.strings))
				bot.say("  %s" % meaning, destination)
				meanings2storage.append(meaning)
			words.append(meanings2storage)

		bot.db.set_plugin_value("rae", word, json.dumps(words))
