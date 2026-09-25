def restart(args, bot, params: dict, helpStr=False):
    if helpStr:
        return "`/restart` - restarts the bot"
    else:
        if params["author"] == params["env"]["ownerId"]:
            bot.sendMessage(params["channel"], "Restarting bot ...")
            bot.flags.add("restart")
        else:
            bot.sendMessage(params["channel"], "Missing Permisions")

def forceStatsSave(args, bot, params: dict, helpStr=False):
    if helpStr:
        return "`/forcestatssave` - forcing the stats save (will not influence the saving cycle)"
    else:
        if params["author"] == params["env"]["ownerId"]:
            bot.log("Saving stats ...")
            with open("stats.json", "w", encoding="utf-8") as f:
                json.dump(bot.stats, f, ensure_ascii=False, indent=4)
            bot.log("Stats saved")
        else:
            bot.sendMessage(params["channel"], "Missing Permisions")
