import synth.forAll as forAll

class commandExecutor:
    def __init__(self, bot):
        self.bot = bot
        self.commandTable = {"stats": forAll.stats,
                             "help": forAll.chelp,
                             "dice": forAll.dice}
    
    def execute(self, packet):
        command: str = packet["content"].strip().strip("/").split(" ")
        try:
            self.commandTable[command[0]](command[1:], self.bot, {"channel":packet["channel"], "author": packet["author"]})
        except: pass