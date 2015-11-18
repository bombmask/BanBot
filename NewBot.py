
import twitchtools.chat.IRC_DB as IRCT
import twitchtools.chat.EventHandler as EH
from twitchtools.login.profiles import Profile
from twitchtools.chat import ChannelStorage as CS
import datetime
import json
import requests
import time
# Example classes

superUsers = ["bomb_mask"]


class BasicBanEvent(EH.EventHandler):
    TYPE = EH.TEvent.CLEARCHAT

    @classmethod
    def Execute(cls, ref, *message):
        data = ref.ChannelData(message[1].params[0])
        data.banAmount += 1

        ref.dftCursor.execute(
            "INSERT INTO bans VALUES (?,?,?)",
            (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), message[1].GetMessage(), False)
        )

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

class KappaCommand(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):
        tm = message[1]
        if (tm.GetMessage().startswith("-kc") and
            (
                tm.GetTags().get("user-type") == "mod" or
                tm.GetTags().get("display-name").lower() == tm.params[0][1:] or
                tm.GetTags().get("display-name").lower() in superUsers
            )):
            # Execute command for mod, super user, or owner
            # Configure section
            parts = tm.GetMessage().split(" ")[1:]
            if parts[0] == "ban":
                print(parts[1:])
                ref.ChannelData().bannedWords += parts[1:]
                print("wordlist",parts)
            elif parts[0] == "message":
                ref.ChannelData().kMessage = " ".join(parts[1:])



            return #Don't check for banned words

        splicedMessage = tm.GetMessage().split(' ')

        print("searching ",splicedMessage)
        for word in ref.ChannelData(tm.params[0]).bannedWords:
            print("comparing", word)
            if word in splicedMessage:
                print("found word")
                break
        else:
            print("no words,exiting")
            return

        try:
            USER = ref.ChannelData(tm.params[0]).Users[tm.GetTags().get("display-name").lower()]
        except KeyError:
            USER = ref.ChannelData(tm.params[0]).InitalizeNewUser(tm.GetTags().get("display-name").lower())

        exec("seconds = "+ref.ChannelData(tm.params[0]).timeCurve.format(times=USER.bannedWordCount))
        ref.PrivateMessage(tm.params[0], "timeout {} {}".format(tm.GetTags().get("display-name").lower(), seconds))


    @classmethod
    def Once(cls, ref):
        CS.ChannelData.kMessage = ""
        CS.ChannelData.purgeAmount = 0
        CS.ChannelData.bannedWords = []
        CS.ChannelData.timeCurve = "{times}^2"
        CS.UserData.bannedWordCount = 0

        ref.CreateTable("UserData", "User TEXT, Channel TEXT, DATA TEXT")



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



if __name__ == '__main__':
    twitch = IRCT.IRC_DB()

    twitch.Register(BasicBanEvent )
    twitch.Register(JoinCommand)
    twitch.Register(LeaveCommand)


    twitch.flags["write"] = True
    cProfile = Profile("bombmask")
    twitch.username = cProfile.name
    twitch.password = cProfile.password
    twitch.serverPair = ("irc.twitch.tv", 6667)
    twitch.Start()
    twitch.Request("twitch.tv/tags")
    twitch.Request("twitch.tv/commands")


    twitch.Join("bomb_mask")


    #print("entering mainloop")
    try:
        twitch.MainLoop()
    except KeyboardInterrupt as E:
        pass

    twitch.Close()
