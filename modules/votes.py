import json
import re
import time
import shlex
from sopel import module

VOTE_FORMAT_SINGLE = "%(id)s) \"%(voteName)s\" propuesta por %(proposer)s en [%(created)s]: Votos: positivos (%(positiveVotes)s) - negativos (%(negativeVotes)s) - Notas: %(note)s"
VOTE_FORMAT_MULTI = "%(id)s) \"%(voteName)s\" propuesta por %(proposer)s en [%(created)s] - Notas: %(note)s - %(options)s"
MULTI_TEMPLATE = "%(key_id)s) %(name)s [positivos:%(positiveVotes)s - negativos:%(negativeVotes)s]"
DATETIME_FORMAT = "%Y/%m/%d"
PLUGIN_NAME = "votes"
PLUGIN_INFO = "%s_info" % (PLUGIN_NAME)
NOTE_DEFAULT_VALUE = "No hay notas en esta propuesta."
TYPE_DEFAULT_VALUE = "single"

@module.commands("createVote")
@module.example(".createVote <Propuesta> [single/multi[:[opción1[,opción2,...]]]] [nota]")
def createVote(bot, trigger):
    """Escribir una propuesta."""

    args = shlex.split(trigger.group(2))[:3]

    if (args == []):
        bot.reply("Por favor, siga la sintaxis.")
        return

    note = None
    type = None

    if (len(args) == 3):
        (voteName, type, note) = args
    elif (len(args) == 2):
        (voteName, type) = args
    else:
        (voteName,) = args

    if (note is None):
        note = NOTE_DEFAULT_VALUE

    if (type is None):
        type = TYPE_DEFAULT_VALUE

    multi_value = {}
    if not (re.match(r"^(single|multi:(.+)+,*)", type)):
        bot.reply("¡No está siguiendo el formato apropiado!")
        return
    else:
        type_ = type
        type = type[:6]
        if (type == "multi:"):
            multi_value_ = [x.strip() for x in type_[6:].split(",")]
            multi_value_ = [x for x in multi_value_ if (x)]

            if (multi_value_ == []):
                bot.reply("Debes escribir las opciones.")
                return

            multi_value = {}
            for i, v in enumerate(multi_value_, 1):
                multi_value[i] = {
                    "name"          : v,
                    "positiveVotes" : 0,
                    "negativeVotes" : 0
                }

    if (bot.db.get_plugin_value(PLUGIN_NAME, voteName) is not None):
        bot.reply("La propuesta ya existe.")
        return

    plugins_info = bot.db.get_plugin_value(PLUGIN_INFO, "list", [])
    if (plugins_info != []):
        plugins_info = json.loads(plugins_info)
    plugins_info.append(voteName)

    vote_info = {
        "proposer"      : trigger.nick.lower(),
        "note"          : note,
        "created"       : time.strftime(DATETIME_FORMAT),
        "positiveVotes" : 0,
        "negativeVotes" : 0,
        "votes"         : [],
        "type"          : type,
        "multi_value"   : multi_value
    }

    bot.db.set_plugin_value(PLUGIN_NAME, voteName, json.dumps(vote_info))
    bot.db.set_plugin_value(PLUGIN_INFO, "list", json.dumps(plugins_info))
    bot.reply("La propuesta \"%s\" ha sido creada con éxito." % (voteName))

@module.commands("vote")
@module.example(".vote <propuesta> <-/+>[Número de la opción]")
def vote(bot, trigger):
    """Vota para propuesta específica."""
    
    args = shlex.split(trigger.group(2))[:2]

    if (args == []):
        bot.reply("Por favor, siga la sintaxis.")
        return

    pos_or_neg = None
    option = "+"
    index = -1

    if (len(args) == 2):
        (voteName, option) = args
    else:
        (voteName,) = args

    proposal = bot.db.get_plugin_value(PLUGIN_NAME, voteName)
    if (proposal is None):
        bot.reply("La propuesta no existe.")
        return

    vote_info = json.loads(proposal)

    if (trigger.nick.lower() in vote_info["votes"]):
        bot.reply("¡Ya votaste, no puedes votar otra vez en esta propuesta!")
        return

    pos_or_neg = option[:1]
    if (pos_or_neg == "+"):
        vote_type = "positiveVotes"
    elif (pos_or_neg == "-"):
        vote_type = "negativeVotes"
    else:
        bot.reply("¡El voto debe ser positivo o negativo!")
        return

    option = option[1:].strip()

    if (vote_info["type"] == "single"):
        vote_info[vote_type] += 1
    else:
        if not (option):
            bot.reply("Es necesario escribir la opción.")
            return

        multi_value = vote_info["multi_value"]
        if (multi_value.get(option) is None):
            bot.reply("La opción no existe para esta propuesta.")
            return
        else:
            multi_value[option][vote_type] += 1
            vote_info["multi_value"] = multi_value
 
    vote_info["votes"].append(trigger.nick.lower())

    bot.db.set_plugin_value(PLUGIN_NAME, voteName, json.dumps(vote_info))
    bot.reply("¡Nos complace que hayas votado!")

@module.commands("listVotes")
@module.example(".listVotes")
def listVotes(bot, trigger):
    """Listar las propuestas hechas."""

    plugins_info = bot.db.get_plugin_value(PLUGIN_INFO, "list", [])
    if (plugins_info != []):
        plugins_info = json.loads(plugins_info)

    id = 0
    for voteName in plugins_info:
        id += 1
        vote_info = json.loads(bot.db.get_plugin_value(PLUGIN_NAME, voteName))

        id_str = "%d" % (id)

        if (vote_info["type"] == "single"):
            positiveVotes_str = "%d" % (vote_info["positiveVotes"])
            negativeVotes_str = "%d" % (vote_info["negativeVotes"])

            bot.say(VOTE_FORMAT_SINGLE % {
                "id"            : id_str,
                "voteName"      : voteName,
                "proposer"      : vote_info["proposer"],
                "created"       : vote_info["created"],
                "positiveVotes" : positiveVotes_str,
                "negativeVotes" : negativeVotes_str,
                "note"          : vote_info["note"]
            })
        else:
            options = []

            for key_id, option_dict in vote_info["multi_value"].items():
                positiveVotes_str = "%d" % (option_dict["positiveVotes"])
                negativeVotes_str = "%d" % (option_dict["negativeVotes"])

                options.append(MULTI_TEMPLATE % {
                    "key_id"        : key_id,
                    "name"          : option_dict["name"],
                    "positiveVotes" : positiveVotes_str,
                    "negativeVotes" : negativeVotes_str
                })
            options_str = ", ".join(options)

            bot.say(VOTE_FORMAT_MULTI % {
                "id"            : id_str,
                "voteName"      : voteName,
                "proposer"      : vote_info["proposer"],
                "created"       : vote_info["created"],
                "note"          : vote_info["note"],
                "options"       : options_str
            })

    if (id == 0):
        bot.reply("Lo siento, pero no hay votaciones.")

@module.commands("delVote")
@module.example(".delVote <Propuesta>")
def delVote(bot, trigger):
    """Borrar una propuesta."""

    args = shlex.split(trigger.group(2))[:1]

    if (args == []):
        bot.reply("Por favor, siga la sintaxis.")
        return
    else:
        voteName = args[0]
    
    if (bot.db.get_plugin_value(PLUGIN_NAME, voteName) is None):
        bot.reply("La propuesta not existe.")
        return
    else:
        vote_info = json.loads(bot.db.get_plugin_value(PLUGIN_NAME, voteName))

        if (trigger.nick.lower() != vote_info["proposer"]):
            bot.reply("¡No te permito que elimines esta propuesta ya que no la creaste! ¡Fuera!")
            return

    plugins_info = bot.db.get_plugin_value(PLUGIN_INFO, "list")
    plugins_info = json.loads(plugins_info)
    plugins_info.pop(plugins_info.index(voteName))

    bot.db.delete_plugin_value(PLUGIN_NAME, voteName)
    bot.db.set_plugin_value(PLUGIN_INFO, "list", json.dumps(plugins_info))
    bot.reply("¡Se ha borrado una propuesta!")
