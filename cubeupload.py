import logging
import requests
from sopel import module
from sopel import formatting
from sopel.formatting import colors

URL = "https://u.cubeupload.com/{username}/{img_name}"

@module.commands("cubeupload")
@module.example(".cubeupload <Nombre de usuario> <Nombre de la imagen>")
def cubeupload(bot, trigger):
	"""Proporciona o muestra (si es el cliente de Hirana) una imagen alojada en cubeupload"""

	user = trigger.group(3)
	img_name = trigger.group(4)

	if (user is None) or (img_name is None):
		bot.say(formatting.color("Por favor, escriba el nombre de usuario y de la imagen en cuestión.", colors.YELLOW))
	else:
		img_url = URL.format(
			username=user,
			img_name=img_name
		)
		r = requests.head(img_url)
		if (r.status_code == 200):
			bot.say(img_url)
		elif (r.status_code == 404):
			bot.say(formatting.color("Imagen no encontrada.", colors.RED))
		else:
			bot.say(formatting.color("No se qué pasó. Pregunta al administrador.", colors.YELLOW))
			r.raise_for_status()
