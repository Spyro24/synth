import time
import datetime
import base64
import synth.wssClient as wssClient
import json
import synth.commands as commands
import requests

class bot:
    def __init__(self, token):
        self.logChannel = "01KHDS86KVYX5KDWY6HEG730VY"
        self.botToken = token
        self.log("Starting Bot")
        #self.logFile = open(f"{}.log", "a")
        #self.logFile.write(encrypt_string_with_public_key("Logging start", self.logPublicKey) + "\n")
        self.config = {}
        self.stats = {"allTime":{"messages": 0, "messagesFromMembers":{}}}
        self.websocket = wssClient.WSSClient(f"wss://stoat.chat/events?version=1&format=json&token={self.botToken}")
        self.commandExecutor = commands.commandExecutor(self)
        self.backupScheduleSeconds = 60 * 30
        self.lastBackup = time.time() + self.backupScheduleSeconds
        self.nextPing = 0
        self.userNameLookUpTable = {}
        self.autoResponseBeginns = {"hai","hello","hallo", "hey"}
        self.channelToServerResolve = dict()
        self.userId = requests.get("https://stoat.chat/api/users/@me", headers={"X-Bot-Token": self.botToken}).json()["_id"]
        self.ready()
    
    def ready(self):
        self.log("Restoring Stats")
        self.loadStats()
        self.log("Stats restored")
        self.log("Login")
        init = True
        while init:
            if self.websocket.has_new_data():
                for packet in self.websocket.get_messages():
                    packet = json.loads(packet)
                    if packet["type"] == "Ready":
                        for channel in packet["channels"]:
                            if "server" in channel:
                                self.channelToServerResolve[channel["_id"]] = channel["server"]
                        self.log("Loged In")
                        init = False
        self.mainLoop()
    
    def mainLoop(self):
        loop = True
        while loop:
            time.sleep(0.1)
            if time.time() > self.lastBackup:
                self.lastBackup = time.time() + self.backupScheduleSeconds
                self.log("Saving Stats")
                with open("stats.json", "w", encoding="utf-8") as f:
                    json.dump(self.stats, f, ensure_ascii=False, indent=4)
            if self.websocket.has_new_data():
                for packet in self.websocket.get_messages():
                    continueFlag = False
                    packet = json.loads(packet)
                    if packet["type"] == "Message" and "content" in packet:
                        if packet["author"] == self.userId:
                            continue
                        message: str = packet["content"].strip()
                        words = message.split(" ")
                        #if len(words) == 1 and words[0].lower() in self.autoResponseBeginns:
                        #    self.replyToMessage(packet["channel"], f"{words[0]} <@{packet['author']}>", packet["_id"])
                        for word in words:
                            if word.startswith("<@") and word.endswith(">"):
                                if "member" in packet and "roles" in packet["member"]:
                                    break
                                if (not packet["author"] in self.stats["allTime"]["messagesFromMembers"]) or self.stats["allTime"]["messagesFromMembers"][packet["author"]] < 5:
                                    self.kickUser(packet["author"], self.channelToServerResolve[packet["channel"]])
                                    self.log(f"user <@{packet['author']}> auto kicked, prob a bot user, message: `{message}`")
                                    continueFlag = True
                        if continueFlag:
                            continue 
                        if len(message) > 0 and message[0] == "/":
                            self.log(f"{packet['author']} used '{message}'")
                            self.commandExecutor.execute(packet)
                        elif any(n in message for n in ("@​everyone", "@everyone")):
                            if not packet["author"] in self.stats["allTime"]["messagesFromMembers"]:
                                self.bannUser(packet["author"], self.channelToServerResolve[packet["channel"]], "Pinging Everyone")
                        else:
                            self.stats["allTime"]['messages'] += 1
                            if packet["author"] in self.stats["allTime"]["messagesFromMembers"]:
                                self.stats["allTime"]["messagesFromMembers"][packet["author"]] += 1
                            else:
                                self.stats["allTime"]["messagesFromMembers"][packet["author"]] = 1
            if self.nextPing < time.time():
                self.websocket.send_data('{"type":"Ping","data":' + str(time.time()) + '}')
                self.nextPing = time.time() + 10
                            
    
    def sendMessage(self, channel: str, message: str):
        requests.post(f"https://stoat.chat/api/channels/{channel}/messages?", headers={"X-Bot-Token": self.botToken}, json={"content": message})
    
    def replyToMessage(self, channel: str, message: str, replyTo: str):
        requests.post(f"https://stoat.chat/api/channels/{channel}/messages?", headers={"X-Bot-Token": self.botToken}, json={"content": message,"replies":[{"id":replyTo,"mention":True}]})
    
    def lookUpUserName(self, userID: str):
        try:
            return self.userNameLookUpTable[userID]
        except KeyError:
            resp = requests.get(f"https://stoat.chat/api/users/{userID}", headers={"X-Bot-Token": self.botToken})
            if resp.ok:
                resp = resp.json()
                self.userNameLookUpTable[userID] = resp["username"]
                return self.userNameLookUpTable[userID]
            return None
    
    def bannUser(self, userID, serverID, reason=""):
        requests.put(f"https://stoat.chat/api/servers/{serverID}/bans/{userID}", headers={"X-Bot-Token": self.botToken}, json={"reason":reason,"delete_message_seconds":1200})
    
    def kickUser(self, userID, serverID, reason=""):
        requests.delete(f"https://stoat.chat/api/servers/{serverID}/members/{userID}", headers={"X-Bot-Token": self.botToken})
    
    def loadStats(self):
        stats = {}
        try:
            with open("stats.json", "r", encoding="utf-8") as f:
               stats = json.load(f) or {}
            self.stats['allTime'] = stats["allTime"]
        except: pass
    
    def log(self, msg):
        logTime = time.gmtime()
        logEntry = f"[{logTime[0]}-{logTime[1]}-{logTime[2]} {logTime[3]}:{logTime[4]}:{logTime[5]}] {msg}"
        print(logEntry)
        self.sendMessage(self.logChannel, logEntry)
