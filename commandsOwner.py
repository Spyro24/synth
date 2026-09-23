def restart(args, bot, params: dict, helpStr=False):
    if helpStr:
        return "`/restart` - restarts the bot"
    else:
        if params["author"] == params["env"]["ownerId"]:
            bot.sendMessage(params["channel"], "Restarting bot ...")
            bot.restart()
        else:
            bot.sendMessage(params["channel"], "Missing Permisions")