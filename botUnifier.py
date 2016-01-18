import twitchtools.chat.IRC_Twitch as IRC
import twitchtools.chat.EventHandler as EH


import sqlite3 as sql
import requests
from enum import Enum

class SERVER(Enum):
    BOTH = 0
    WHISPER = 1
    TMI = 2

class BotCommand(EH.EventHandler):
    bHasBeenAdded = False
    SType = SERVER.BOTH

    def AddMe(self, ref):
        self.BOT = ref
        self.bHasBeenAdded = True

class printAll(BotCommand):
    TYPE = EH.TEvent.ALL


    def Execute(self, ref, *message):
        print(message[1].GetRaw())

class logDBAll(BotCommand):
    TYPE = EH.TEvent.ALL

    def Execute(self, ref, *message):
        try:
            cursor = self.BOT.GetCursor()
            cursor.execute(
                "INSERT INTO chatdata VALUES (?,?,?,?,?,?)",
                (
                    ref.tMessage.prefix.split('!')[0],
                    str(message[0]),
                    ref.tMessage.GetTime(),
                    ref.tMessage.GetEvent().value,
                    ref.tMessage.params[0],
                    ref.tMessage.GetMessage()
                )
            )
            self.BOT.Commit()
            cursor.close()

        except sql.Error as E:
            print("An Error occured:",E.args[0])

class BotBase(object):

    def __init__(self):

        self.twitchLink = IRC.IRC_Twitch(self)
        self.whisperLink = IRC.IRC_Twitch(self)

        self.servers = [self.twitchLink, self.whisperLink]

        self.username = ""
        self.password = ""
        self.flags = {}

        self.pairTwitch = []
        self.pairWhisper = []

        self.tagsAll = []
        self.tagsTwitch = []
        self.tagsWhisper = []

        self.CommandInsts = {}

    def Start(self):
        self.twitchLink.serverPair = self.pairTwitch
        self.whisperLink.serverPair = self.pairWhisper

        for server in self.servers:
            server.username = self.username
            server.password = self.password
            server.flags = self.flags
            #server.RegisterClass(printAll)

            server.Start()


        for tag in set(self.tagsTwitch + self.tagsAll):
            self.twitchLink.Request(tag)

        for tag in set(self.tagsWhisper + self.tagsAll):
            self.whisperLink.Request(tag)

    def Stop(self):
        for server in self.servers:
            server.Close()

    def Register(self, RegClass):
        self.CommandInsts[RegClass] = RegClass()
        self.CommandInsts[RegClass].AddMe(self)

        if RegClass.SType is SERVER.BOTH or RegClass.SType is SERVER.TMI:
            self.twitchLink.RegisterObject(self.CommandInsts[RegClass])

        if RegClass.SType is SERVER.BOTH or RegClass.SType is SERVER.WHISPER:
            self.whisperLink.RegisterObject(self.CommandInsts[RegClass])

    def Whisper(self, user, *message):
        self.whisperLink.PrivateMessage("_themaskoftruth_1444811826692", "/w {} {}".format(user, " ".join(message)))

class BotDB(BotBase):
    def __init__(self, DBName="config/bot.db"):
        super().__init__()
        self.dbConn = sql.connect(DBName, check_same_thread=False)

        self.dftCursor = self.dbConn.cursor()
        self.CreateTable("chatdata", "User TEXT, Raw TEXT, Time DATE, Event INT, Channel TEXT, Message TEXT")
        self.CreateTable("config", "channel TEXT, json TEXT")

        print("Current SQLite Version: ", sql.sqlite_version)

        self.Register(logDBAll)
        self.Register(printAll)

    def Load(self):
        pass

    def Save(self):
        pass

    def CreateTable(self, tableName, typeString):
        executeString = "create table if not exists {} ({})".format(tableName, typeString)
        self.dftCursor.execute(executeString)

    def GetCursor(self):
        return self.dbConn.cursor()

    def Commit(self):
        self.dbConn.commit()
