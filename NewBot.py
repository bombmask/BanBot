
import twitchtools.chat.IRC_DB as IRCT
import twitchtools.chat.EventHandler as EH
from twitchtools.login.profiles import Profile
from twitchtools.chat import ChannelStorage as CS
import datetime
import json
import requests
import time
import BotWeb
import threading

from command import Command, AwareCommand, PERMLEVEL as cmdPERMISSION
import botUnifier
# Example classes

superUsers = ["bomb_mask"]


class BasicBanEvent(EH.EventHandler):
    TYPE = EH.TEvent.CLEARCHAT

    @classmethod
    def Execute(cls, ref, *message):
        data = ref.ChannelData(message[1].params[0])
        data.banAmount += 1
        cursor = ref.GetCursor()
        cursor.execute(
            "INSERT INTO bans VALUES (?,?,?)",
            (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), message[1].GetMessage(), False)
        )
        self.BOT.Commit()
        cursor.close()

    @classmethod
    def Once(cls, ref):
        ref.CreateTable("bans", "Time TEXT, User TEXT, Us BOOL DEFAULT true")
        CS.ChannelData.banAmount = 0

class BasicStats(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):
        if message[1].GetMessage().lower() == "-hi" and tm.GetTags().get("display-name").lower() in superUsers:
            ref.PrivateMessage(message[1].params[0][1:], ref.ChannelData(message[1].params[0]).banAmount)

    @classmethod
    def Once(cls, ref):
        pass

class KappaCommand(botUnifier.BotCommand):
    TYPE = EH.TEvent.PRIVMSG
    COMMAND = AwareCommand("-","kc", requirements=[cmdPERMISSION.HOST,cmdPERMISSION.SUPERUSER,cmdPERMISSION.MOD])

    def Execute(self, ref, *message):
        if not self.bHasBeenAdded:
            raise RuntimeError("This command has not be pre registered")

        tm = message[1]
        if self.COMMAND.Test(tm):
            self.Configure(tm)
            return #Don't check for banned words

        splicedMessage = tm.GetMessage().split(' ')

        for word in ref.ChannelData(tm.params[0]).bannedWords:
            if word in splicedMessage:
                break
        else:
            return

        USER = ref.ChannelData().GetUser(tm.GetTags().get("display-name"))

        seconds = eval(ref.ChannelData().timeCurve.format(times=int(USER.bannedWordCount)))

        ref.PrivateMessage(tm.params[0][1:], "/timeout {} {}".format(tm.GetTags().get("display-name").lower(), seconds))

        USER.bannedWordCount += 1
        ref.ChannelData().purgeAmount += 1

        self.BOT.Whisper(tm.GetTags()["display-name"], ref.ChannelData().kMessage)

        if ref.ChannelData().purgeAmount % ref.ChannelData().PublicSpeak:
            ref.PrivateMessage(tm.params[0], ref.ChannelData().kMessage)

    def Configure(self, message):
        # Execute command for mod, super user, or owner
        # Configure section
        parts = message.GetMessage().split(" ")[1:]
        if parts[0] == "ban":
            ref.ChannelData().bannedWords.update(parts[1:])

        elif parts[0] == "message":
            ref.ChannelData().kMessage = " ".join(parts[1:])

        elif parts[0] == "time":
            ref.ChannelData().timeCurve = "".join(parts[1:])

        elif parts[0] == "list":
            ref.PrivateMessage(message.params[0],*ref.ChannelData().bannedWords)

    @classmethod
    def Once(cls, ref):
        CS.ChannelData.PublicSpeak = 10
        CS.ChannelData.kMessage = ""
        CS.ChannelData.purgeAmount = 0
        CS.ChannelData.bannedWords = set()
        CS.ChannelData.timeCurve = "300*{times}+10"
        CS.UserData.bannedWordCount = 0

        #ref.CreateTable("UserData", "User TEXT, Channel TEXT, DATA TEXT")

class JoinCommand(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):

        if message[1].GetMessage().lower().startswith("-join") and message[1].GetTags().get("display-name").lower() in superUsers:
            ref.Join(message[1].GetMessage().split(" ",2)[1])

class LeaveCommand(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):
        if message[1].GetMessage().lower().startswith("-leave") and message[1].GetTags().get("display-name").lower() in superUsers:
            ref.Leave(message[1].GetMessage().split(" ",2)[1])

class JoinLargest(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):
        if message[1].GetMessage().lower().startswith("-joinall") and message[1].GetTags().get("display-name").lower() in superUsers:
            total = 0
            channels = requests.get("https://api.twitch.tv/kraken/streams?limit={}".format(int(message[1].GetMessage().split(" ",2)[1]))).json()
            for i in range(int(message[1].GetMessage().split(" ",2)[1])):
                ref.Join(channels["streams"][i]["channel"]["display_name"])
                channel = channels["streams"][i]
                total += int(channel["viewers"])
                print("Joining channel {} with {} viewers".format(channel["channel"]["display_name"], channel["viewers"]))
                if i%10 == 0:
                    time.sleep(4)
            print("total {} viewers :",total)

class TestWhisper(botUnifier.BotCommand):
    TYPE = EH.TEvent.PRIVMSG
    COMMAND = Command(":", "whisperme")

    def Execute(self, ref, *msg):
        if not self.bHasBeenAdded:
            raise RuntimeError("This command has not be pre registered")

        if not self.COMMAND.Test(msg[1].GetMessage()):
            return

        self.BOT.Whisper(msg[1].GetTags().get("display-name", "bombmask"), "Hello world!")



if __name__ == '__main__':
    WebServer = BotWeb.WebServer()

    m = botUnifier.BotDB()
    WebServer.AddMe(m)
    WebServer.MainLoop()

    m.flags["write"] = True
    cProfile = Profile("bombmask", "OAUTHS")
    m.username = cProfile.name
    m.password = cProfile.password
    m.pairTwitch = ("irc.twitch.tv", 6667)
    """
    ["199.9.253.119","199.9.253.120", "10.1.222.247","192.16.64.213",
    "192.16.64.182", "199.9.255.149", "192.16.64.173", "199.9.255.148",
    "192.16.64.181", "199.9.255.146", "92.16.64.214", "199.9.255.147"]
    """
    m.pairWhisper = ("199.9.253.119", 6667)

    m.tagsAll = ["twitch.tv/tags", "twitch.tv/commands"]

    m.twitchLink.RegisterClass(JoinCommand)
    m.twitchLink.RegisterClass(LeaveCommand)
    m.Register(TestWhisper)
    m.Register(KappaCommand)

    m.Start()

    m.twitchLink.Join("bomb_mask")

    m.whisperLink.MainLoop(fork=True)

    try:
       m.twitchLink.MainLoop()

    except KeyboardInterrupt as E:
        pass

    m.Stop()
    # twitch = IRCT.IRC_DB()
    #
    # twitch.Register(BasicBanEvent )
    # twitch.Register(JoinCommand)
    # twitch.Register(LeaveCommand)
    #
    #
    # twitch.flags["write"] = True
    # cProfile = Profile("bombmask")
    # twitch.username = cProfile.name
    # twitch.password = cProfile.password
    # twitch.serverPair = ("irc.twitch.tv", 6667)
    # twitch.Start()
    # twitch.Request("twitch.tv/tags")
    # twitch.Request("twitch.tv/commands")
    #
    #
    # twitch.Join("bomb_mask")
    #
    #
    # #print("entering mainloop")
    # try:
    #     twitch.MainLoop()
    # except KeyboardInterrupt as E:
    #     pass
    #
    # twitch.Close()
