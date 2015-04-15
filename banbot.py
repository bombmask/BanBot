from twitchtools import login, chat, utils
import collections
import socket
import threading
import time
import datetime
import requests
import webbrowser
import json

twitchlink = ("irc.twitch.tv",6667)

bb_info = {"header":"BanBot Distro TheMaskOfTruthv1"}

SUPER_USERS = ["bomb_mask", "batedurgonnadie"]

utils.Printer.ON = True
utils.Printer.level = "DEBUG"




class banObject(object):

    def __init__(self, t_user):
        self.id = t_user.name
        self.user = t_user
        self.creation_time = datetime.datetime.now()
        self.ban_times = [self.creation_time,]

        self.p = utils.Printer("BanObject.{}".format(self.user.name))

        #self.p("CREATED BAN OBJECT")


    def __str__(self):
        return "BanObject of [{}]".format(self.user.name)

    def __repr__(self):
        return "BanObject of [{}]".format(self.user.name)

    def toMarkdown(self):
        self.p("TO MARKDOWN CALLED")
        message_list = ""

        last = datetime.datetime.now()

        for msg in self.user.messages:
            try:
                message_list +=  ">> Banned/timedout at {}\n".format(self.banTimeBetween(last, msg.creation_time).strftime('%Y-%m-%d %H:%M:%S'))
            except AttributeError:
                pass

            last = msg.creation_time

            message_list += " {}\n".format(self.messageToString(msg))

        inter = """### {user}\n```\n{messageList}\n```\n""".format(user = self.user.name, messageList=message_list)
        return inter

    def messageToString(self, message):
        return "[{}] :{}".format(message.time(), message.message)

    def append(self):
        self.ban_times.append(datetime.datetime.now())

    def banTimeBetween(self, last, new):
        for i in self.ban_times:
            if last <= i and i <= new:
                return i

        return ""

def BanBotRuntime(channel, message):

    p = utils.Printer("BanBotRuntime")

    target_user = channel.users[message.target]

    try:

        BanBotRuntime.bans[target_user.name].append()

    except KeyError:
        BanBotRuntime.bans[target_user.name] = banObject(target_user)

    except AttributeError:
        BanBotRuntime.bans = collections.OrderedDict()
        BanBotRuntime.bans[target_user.name] = banObject(target_user)

    except Exception, e:
        p(e)


def BanBotRequest(channel, message):
    p = utils.Printer("BanBot.report")

    #File Generation
    gist = ""
    #write Header
    gist += "# {}\n".format(bb_info["header"])
    gist += "Ban Report Generated at [{}]\n".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    #Write User links
    gist += "## User Report Issued - {} total users banned\n".format(sum(1 for item in BanBotRuntime.bans.values()))

    for user in BanBotRuntime.bans.values():
        gist += "- [{user}](#{user})\n".format(user = user.user.name)

    gist += "\n"

    #Write User header - message
    for ban in BanBotRuntime.bans.values():
        gist += ban.toMarkdown()



    #Github gist
    gistDict = {
        "files": {"bans.md": {"content" : gist}},
        "description": "{}".format("automated ban report created at "+datetime.datetime.now().strftime('%Y-%m-%d %H:%M::%S')),
        "public": True
    }

    r = requests.post("https://api.github.com/gists", data=json.dumps(gistDict)).json()
    channel.pm(r["html_url"] + " " + "@" + message.user)

    p(r["url"])



class banbot(utils.Operator):
    @classmethod
    def poll(self, *args):
        return args[1].command == "CLEARCHAT" or (args[1].message == ":clear" and args[1].user in SUPER_USERS)

    def execute(self, *args):
        BanBotRuntime(*args)

class banBotReporter(utils.Operator):
    @classmethod
    def poll(self, *args):
        return (args[1].command == "PRIVMSG" and args[1].message.startswith(":markdown") and hasattr(BanBotRuntime, "bans") and args[1].user == (args[0].owner))

    @classmethod
    def reason(self, *args):
        reasons = set()
        if args[1].command == "PRIVMSG":
            reasons.add("Command is not PRIVMSG")

        if args[1].message.startswith(":markdown"):
            reasons.add("Message does not start with :markdown")

        if hasattr(BanBotRuntime, "bans"):
            reasons.add("Function(Channel) does not have any bans")

        return reasons



    def execute(self, *args):
        BanBotRequest(*args)

class cleanReport(utils.Operator):
    @classmethod
    def poll(self, *args):
        return (args[1].command == "PRIVMSG" and args[1].message.startswith(":clean") and hasattr(BanBotRuntime, "bans") and args[1].user == (args[0].owner))

    def execute(self, *args):
        channel, message = args
        BanBotRuntime.bans = collections.OrderedDict()
        channel.pm("Cleaned bans list... Starting fresh @{} (local time)".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M::%S')))


class GeneralMessageOp(utils.Operator):

    def __init__(self):
        self.callTimes = 0
        self.p = utils.Printer("GeneralMessage")

    @classmethod
    def poll(self, *args):
        return (args[1].command == "PRIVMSG")

    def execute(self, *args):
        channel, message = args
        self.callTimes += 1
        self.p.addSpecial(channel.name)
        self.p("instance called", self.callTimes)


p = utils.Printer("MAINLOOP")
with chat.IRC(twitchlink, login.Profile("themaskoftruth")) as twitch:
    twitch.capibilities("tags")
    twitch.capibilities("commands")
    twitch.join("bomb_mask, snarfybobo")
    twitch.register(banbot)
    twitch.register(banBotReporter)
    twitch.register(cleanReport)


    for i in twitch.readfile():
        if i.command == "PRIVMSG":

            if i.message == "QUIT" and i.user in SUPER_USERS:
                twitch.channels["bomb_mask"].pm("Exiting...")
                break

            # if i.message.startswith(":"):
            #     twitch.channels["bomb_mask"].pm(i.message+" "+i.user)
            #     #p("<Sending>", i.message)


        if i.command == "CLEARCHAT":
            p(i.message, i.raw)

