import argparse
from enum import Enum
import twitchtools.chat.MessageParser as MM
class PERMLEVEL(Enum):
    USER=""
    MOD="mod"
    STAFF="staff"
    HOST=0
    SUPERUSER=-1
    ALL=1
    NOTUSER=2

class Command(object):
    DEBUG = False
    SUPERUSERS = ["bomb_mask"]

    def __init__(self, prefix, command, argparse=False, commandIsRegex=False):
        self.prefix = prefix
        self.command = command

        self.argparse = argparse
        self.regex = commandIsRegex
        self.Reinit()
        if not self.Test(self.prefix+self.command):
            print('Command Test did not Succeed...')

    def GetCommand(self):
        return self.prefix+self.command

    def Reinit(self):
        if self.DEBUG:
            self.prefix = self.prefix*2

    def Test(self, msgString):
        if self.argparse:
            return self.TestArgparse(msgString)

        elif self.regex:
            return self.TestRegex(msgString)

        else:
            return self.TestNormal(msgString)

    def TestNormal(self, msgString):
        if self.DEBUG:
            print(msgString)

        if not msgString.startswith(self.prefix):
            return False

        if not msgString[len(self.prefix):].startswith(self.command):
            return False

        return True

    def TestArgparse(self, msgString):
        raise NotImplementedError()

    def TestRegex(self, msgString):
        raise NotImplementedError()

class AwareCommand(Command):
    def __init__(self, prefix, command, argparse=False, commandIsRegex=False, requirements=[]):

        super().__init__(prefix, command, argparse, commandIsRegex)
        self.requirements = requirements

    def TestNormal(self, tm):

        if isinstance(tm, MM.Message):
            if self.DEBUG:
                print(tm.GetMessage())

            if not tm.GetMessage().startswith(self.prefix):
                return False

            if not tm.GetMessage()[len(self.prefix):].startswith(self.command):
                return False

            if self.requirements[0] != PERMLEVEL.ALL:
                for PERM in self.requirements:
                    if PERM == PERMLEVEL.HOST:
                        if tm.GetTags()["display-name"].lower() == tm.params[0][1:].lower():
                            #Found the host :D
                            break
                    elif PERM == PERMLEVEL.SUPERUSER:
                        if tm.GetTags()["display-name"].lower() in self.SUPERUSERS:
                            #Found the superuser
                            break

                    else:
                        if PERM == tm.GetTags()["user-type"]:
                            # User can use command
                            break

                else:
                    # User does not have permissions
                    return False

            return True

        else: #weird failover
            super().TestNormal(tm)

    def TestArgparse(self, msgStr):
        if self.DEBUG:
            print(tm.GetMessage())

        if isinstance(tm, MM.Message):

            if not tm.GetMessage().startswith(self.prefix):
                return False

            if not tm.GetMessage()[len(self.prefix):].startswith(self.command):
                return False

            if self.requirements[0] != PERMLEVEL.ALL:
                for PERM in self.requirements:
                    if PERM == PERMLEVEL.HOST:
                        if tm.GetTags()["display-name"].lower() == tm.params[0][1:].lower():
                            #Found the host :D
                            break
                    elif PERM == PERMLEVEL.SUPERUSER:
                        if tm.GetTags()["display-name"].lower() in self.SUPERUSERS:
                            #Found the superuser
                            break

                    else:
                        if PERM == tm.GetTags()["user-type"]:
                            # User can use command
                            break

                else:
                    # User does not have permissions
                    return False

            return self.argparse.parse_args()

        else: #weird failover
            super().TestNormal(tm)
