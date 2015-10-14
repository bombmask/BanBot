#! /usr/bin/env python3.4
# -*- coding: utf-8 -*-
from twitchtools import login, chat, utils
import collections
import socket
import threading
import time
import datetime
import requests
import webbrowser
import json
import re

import traceback
###########             CONFIG                ###########
twitchlink = ("irc.twitch.tv", 6667)

bb_info = {"header": "BanBot Distro TheMaskOfTruthv1"}

SUPER_USERS = ["bomb_mask", "batedurgonnadie"]

utils.Printer.ON = True
utils.Printer.level = "DEBUG"
###########              END                  ###########

def constructJSON(IRC, Channel=None):
    JsonDict = {}
    #If Channel is named
    if Channel:
        Ob = IRC.channels.get(Channel, False)

        if Ob:
            with open('JSON.json','w') as fout:
                if not Ob.OperatorInstances.get(BanOp, False):
                    return None

                for BanOb in Ob.OperatorInstances[BanOp].bans.values():
                    json.dump({'#'+Channel:BanOb.toJSON()}, fout, default=str, indent=4)

    else:
        with open('JSON.json','w') as fout:
            for Channel in IRC.channels.items():
                if not Channel[1].OperatorInstances.get(BanOp, False):
                    continue

                for BanOb in Channel[1].OperatorInstances[BanOp].bans.values():
                    json.dump({'#'+Channel[0]:BanOb.toJSON()}, fout, default=str, indent=4)


def backup_data(IRC, filename):
    json_total = {}
    json_total["channels"] = {
        channel[1].name : { user[1].name : [message.raw \
                for message in user[1].messages]\
            for user in channel[1].users.items() }\
        for channel in IRC.channels.items()
    }
    #backup all channels
    # for channel in IRC.channels.items():
    #     assert(channel[0] == channel[1].name)
    #
    #     for user in channel[1].users.items():
    #         print(user)
    #         for message in user[1].messages:
    #             print(message)
    #     #json_total["channels"][channel[0]] = }
    with open(filename, 'w') as fout:
        json.dump(json_total, fout, indent=4)


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

    def toJSON(self):
        JSONDICT = {}
        JSONDICT["Messages"] = [{"tags":Message.tags, "message":Message.message, "time":Message.creation_time.isoformat()} for Message in self.user.messages]
        JSONDICT["Clears"] = [C.isoformat() for C in self.ban_times]
        return {self.user.name:JSONDICT}

    def toMarkdown(self):
        #self.p("TO MARKDOWN CALLED")
        message_list = ""

        last = datetime.datetime.now()

        for msg in self.user.messages:
            try:
                message_list +=  " >> Banned/timedout at {}\n".format(self.banTimeBetween(last, msg.creation_time).strftime('%Y-%m-%d %H:%M:%S'))
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


class BanOp(utils.Operator):
    def __init__(self):
        self.p = utils.Printer("BanBotRuntime")
        self.bans = collections.OrderedDict()

    @classmethod
    def poll(cls, *args):
        return (
            args[1].command == "CLEARCHAT" or
            (
                args[1].message == ":clear" and
                args[1].user in SUPER_USERS
            )
        )

    def execute(self, *args):
        #BanBotRuntime(*args)
        channel, message = args
        target_user = channel.users[message.target]

        try:
            self.bans[target_user.name].append()

        except KeyError:
            self.bans[target_user.name] = banObject(target_user)


class ReportOp(utils.Operator):
    def __init__(self):
        self.p = utils.Printer("BanBot.report")

    @classmethod
    def poll(cls, *args):
        return (
            args[1].command == "PRIVMSG" and
            args[1].message.startswith(":markdown") and
            (
                args[1].user == (args[0].owner) or
                args[1].user in SUPER_USERS or
                ( args[1].tags.get("user-type", "") == "mod" )
            )
        )

    def execute(self, *args):
        #BanBotRequest(*args)
            #File Generation
        channel, message = args

        param = message.message.split(' ')
        if len(param) > 1 and message.user in SUPER_USERS:
            channel_to = channel
            try:
                channel = channel.ircParent.channels[param[1]]
            except KeyError:
                self.p("Channel {} does not exist".format(param[1]))
                return None

        UserLists = {
            "Links": [],
            "Markdown": []
        }
        #Generate Lists of users from ban
        for BanObject in channel.OperatorInstances[BanOp].bans.values():
            UserLists["Links"].append("- [{user}](#{user})\n".format(user=BanObject.user.name))
            UserLists["Markdown"].append(BanObject.toMarkdown())

        #Template string for gist and markdown
        gist = "# {header}\nBan Report Generated at [{time}]\n\n## User Report Issued - {amount} Total Users Banned\n{UserLinkList}\n\n{UserMarkdownList}\n".format(
            header=bb_info["header"],
            time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            amount=len(channel.OperatorInstances[BanOp].bans),
            UserLinkList="".join(UserLists["Links"]),
            UserMarkdownList="".join(UserLists["Markdown"])
        )

        #Github gist
        gistDict = {
            "files": {"bans.md": {"content": gist}},
            "description": "{}".format("automated ban report created at "+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            "public": True
        }
        #Post to github
        r = requests.post("https://api.github.com/gists", data=json.dumps(gistDict)).json()

        if len(param) > 1 and message.user in SUPER_USERS:
            channel_to.pm(r["html_url"] + " " + "@" + message.user)
        else:
            channel.pm(r["html_url"] + " " + "@" + message.user)

        self.p(r["url"])


class CleanOp(utils.Operator):
    @classmethod
    def poll(cls, *args):
        return (
            args[1].command == "PRIVMSG" and
            args[1].message.startswith(":clean") and
            hasattr(args[0].OperatorInstances[BanOp], "bans") and
            args[1].user == (args[0].owner)
        )

    def execute(self, *args):
        channel, message = args
        channel.OperatorInstances[BanOp].bans = collections.OrderedDict()
        channel.pm("Cleaned bans list... Starting fresh @{} (local time)".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


class AboutOp(utils.Operator):
    """"""

    def __init__(self):
        self.p = utils.Printer("GeneralMessage")

    @classmethod
    def poll(self, *args):
        return (args[1].command == "PRIVMSG" and args[1].user in SUPER_USERS and args[1].message.startswith("-about"))

    def execute(self, *args):
        channel, message = args
        channel.pm("Twitch chat ban managment bot created by bomb_mask ")


class JoinCommand(utils.Operator):
    @classmethod
    def poll(cls, *args):
        return (
            args[1].command == "PRIVMSG" and
            args[1].message.startswith("!join ") and
            args[1].tags["display-name"].lower() in SUPER_USERS
        )

    def execute(self, *args):
        channel, message = args
        newChannel = message.message.split(" ")[1:]

        channel.ircParent.join(newChannel)
        print("Joined :", newChannel)


class LeaveCommand(utils.Operator):
    @classmethod
    def poll(cls, *args):
        return (
            args[1].command == "PRIVMSG" and
            args[1].message.startswith("!leave ") and
            args[1].tags["display-name"].lower() in SUPER_USERS
        )

    def execute(self, *args):
        channel, message = args
        newChannel = message.message.split(" ")[1]

        channel.ircParent.part(newChannel)
        print("Left :", newChannel)


class KappaRemove(utils.Operator):
    first_run = 0
    init_on_attach = True

    @classmethod
    def ginit(self, *args):
        pass

    def __init__(self):
        self.banned_words = []
        self.ban_count = 0
        self.ban_whisper_message = "/me Reminder: K appa/K eepo/K appapride are all banned here, they show up as *** for everyone else but yourself. Please refrain from using if you do you will get purged/timed out."
        self.term = utils.Printer("KappaRemove")

    @classmethod
    def poll(cls, *args):

        has_banned_word = False
        message_words = args[1].message.split(' ')
        for banned_word in args[0].OperatorInstances.get(KappaRemove).banned_words:
            if banned_word in message_words:
                has_banned_word = True



        return (
            args[1].command == "PRIVMSG" and
            (
                has_banned_word or
                args[1].message.startswith(":kcfg")
            )
        )



    def execute(self, *args):
        channel, message = args
        user = channel.users[message.target]

        #print(message)
        #print(channel.OperatorInstances.get(KappaRemove).banned_words)
        # Priority?
        if message.message.startswith(":kcfg") and (message.tags.get("user-type", "") == "mod" or message.user == channel.owner):
            self.commands(channel, user, message)

        else:
            if not hasattr(user, "banned_word_count"):
                user.banned_word_count = 1
            else:
                user.banned_word_count += 1


            if user.banned_word_count == 1:
                channel.pm("/timeout {} 10".format(user.name))

            elif user.banned_word_count == 2:
                channel.pm("/timeout {} 300".format(user.name))

            elif user.banned_word_count > 2:
                channel.pm("/timeout {} 600".format(user.name))

            user.whisper(self.ban_whisper_message)

            self.ban_count += 1
            if self.ban_count % 10 == 0:
                channel.pm(self.ban_whisper_message)

    def commands(self, channel, user, message):
        try:
            command = message.message.split(' ')[1]
            args = message.message.split(' ')[2:]

            print(command, args)
            if command == "ban":
                self.banned_words += args

            if command == "unban":
                for i in args:
                    try:
                        self.banned_words.remove(i)
                    except ValueError as E:
                        self.term("Word '{}' Does Not Exist".format(E))

            if command == "words":
                channel.pm("The Banned Words Are:",",".join(self.banned_words))

            if command == "whisper":
                user.whisper(self.ban_whisper_message)

            if command == "message":
                self.ban_whisper_message = " ".join(args)

        except Exception as E:
            print(E)


if __name__ == '__main__':

    p = utils.Printer("MAINLOOP")
    with chat.IRC(twitchlink, login.Profile("themaskoftruth")) as twitch:
        twitch.capibilities("tags")
        twitch.capibilities("commands")

        with open("channels.txt") as fin:
            twitch.join(fin.read().strip())

        twitch.register(BanOp)
        twitch.register(ReportOp)
        twitch.register(CleanOp)
        twitch.register(AboutOp)
        twitch.register(LeaveCommand)
        twitch.register(JoinCommand)
        twitch.register(KappaRemove)

        for i in twitch.readfile():
            #p(i.raw,'\n')
            if i.command == "PRIVMSG":
                if i.message == "$channels" and i.user == "bomb_mask":
                    for name, channel in twitch.channels.items():
                        p(name, channel)


                if i.message == "$stop" and i.user == "bomb_mask":
                    twitch.channels["bomb_mask"].pm("Exiting...")
                    break

                if i.message == "$print" and i.user == "bomb_mask":
                    constructJSON(twitch)

                if i.message == "$backup" and i.user == "bomb_mask":
                    backup_data(twitch, "default.json")
                    p("Creating backup.json")

                p(i.raw,i)

                # if i.message.startswith(":"):
                #     twitch.channels["bomb_mask"].pm(i.message+" "+i.user)
                #     #p("<Sending>", i.message)


            if i.command == "CLEARCHAT":
                p(i.message, i.raw)


"""
CAP REQ :twitch.tv/\r\n
"""
