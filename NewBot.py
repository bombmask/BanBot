
import twitchtools.chat.IRC_DB as IRCT
import twitchtools.chat.EventHandler as EH
from twitchtools.login.profiles import Profile
import datetime
# Example classes

class Respond(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):

        ref.PrivateMessage("bomb_mask", len(message[1].GetMessage()))

class PingPong(EH.EventHandler):
    TYPE = EH.TEvent.PING

    @classmethod
    def Execute(cls, ref, *message):
        ref.PrivateMessage("bomb_mask", "PING PONG!")

class Hello(EH.EventHandler):
    TYPE = EH.TEvent.JOIN

    @classmethod
    def Execute(cls, ref, *message):
        ref.PrivateMessage("bomb_mask", "HI!! I'M BOMB")

class BasicBanEvent(EH.EventHandler):
    TYPE = EH.TEvent.CLEARCHAT

    @classmethod
    def Execute(cls, ref, *message):
        ref.dftCursor.execute(
            "INSERT INTO bans VALUES (?,?)",
            (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), message[1].GetMessage())
        )

    @classmethod
    def Once(cls, ref):
        ref.CreateTable("bans", "TIME TEXT, USER TEXT")

if __name__ == '__main__':
    twitch = IRCT.IRC_DB()

    twitch.Register(Respond )
    twitch.Register(BasicBanEvent )


    twitch.flags["write"] = True
    cProfile = Profile("bombmask")
    twitch.username = cProfile.name
    twitch.password = cProfile.password
    twitch.serverPair = ("irc.twitch.tv", 6667)
    twitch.Start()
    twitch.Request("twitch.tv/tags")
    twitch.Request("twitch.tv/commands")


    twitch.Join("bomb_mask")


    print("entering mainloop")
    try:
        twitch.MainLoop()
    except KeyboardInterrupt as E:
        pass

    twitch.Close()
