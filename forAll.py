import random

def stats(args, bot, params: dict, helpStr=False):
    if helpStr:
        return "`/stats {[all]|day|week|month|year} {user}` - zeigt dir die Stats an"
    else:
        sendString = "> ### Server Stats\n"
        if len(args) == 0:
            top10 = sorted(bot.stats['allTime']['messagesFromMembers'].items(), key=lambda kv: kv[1], reverse=True)[:10]
            sendString += f"> Nachrichten: `{bot.stats['allTime']['messages']}`    Regestred Users: `{len(bot.stats['allTime']['messagesFromMembers'].keys())}`\n> \n> \n"
            sendString += f"> **Top Ten Members**\n"
            n = 1
            print(top10)
            for entry in top10:
                sendString += f">`{bot.lookUpUserName(entry[0])}` has a score of `{entry[1]}`\n"
                n += 1
                
        bot.sendMessage(params["channel"], sendString)
            

def chelp(args, bot, params: dict, helpStr=False):
    if helpStr:
        return "`/help` - Ruft diese Hilfe auf"
    
    sendString = "> ### Hilfe für den helper Synth\n"
    for command in bot.commandExecutor.commandTable.keys():
        sendString += "> " + bot.commandExecutor.commandTable[command](None, None, None, helpStr=True) + "\n"
    bot.sendMessage(params["channel"], sendString)

def dice(args, bot, params: dict, helpStr=False):
    if helpStr:
        return "`/dice [min] [max]` - Würf einen kleinen würfel mit den werten von `min` bis `max`"
    
    sendString = ""
    try:
        sendString = f"> <@{params['author']}> roled a {random.randint(int(args[0]), int(args[1]))}"
        bot.sendMessage(params["channel"], sendString)
    except: pass
