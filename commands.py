import synth.forAll as forAll
import synth.commandsOwner as owner

class commandExecutor:
    def __init__(self, bot):
        self.bot = bot
        self.commandTable = {"stats": forAll.stats,
                             "help": forAll.chelp,
                             "dice": forAll.dice,
                             "restart": owner.restart}
    
    def execute(self, packet):
        command: str = packet["content"].strip().strip("/").split(" ")
        try:
            self.commandTable[command[0]](command[1:], self.bot, {"channel":packet["channel"], "author": packet["author"], "env": self.bot.env})
        except: pass
