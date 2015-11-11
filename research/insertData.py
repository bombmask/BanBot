import sqlite3 as sql
import datetime
from twitchtools.chat import MessageParser as MP
import os
import json

def import_data(filename):
    if not os.path.exists(filename):
        print("Returning from import")
        return

    with open(filename) as fin:
        reloaded = json.load(fin)

    conn = sql.connect("NewDb/bot.db")
    cur = conn.cursor()
    total = 0
    for channel, users in reloaded["channels"].items():


        for user in users.items():

            for message in user[1]:
                total += 1
                tm = MP.Message(message[0], datetime.datetime.strptime(message[1], "%Y-%m-%d %H:%M"))
                cur.execute("INSERT INTO chatdata VALUES (?,?,?,?,?,?)",
                    (
                        tm.prefix.split('!')[0],
                        tm.GetRaw(),
                        tm.GetTime(),
                        tm.GetEvent().value,
                        tm.params.split(' ',1)[0],
                        tm.GetMessage()
                    )
                )
                if tm.GetEvent().value == MP.EH.TEvent.CLEARCHAT.value: #Clearchat
                    cur.execute("INSERT INTO bans VALUES (?,?,?)",(tm.GetTime(), tm.GetMessage(), False))

        conn.commit()
    print("total ",total)


    print("Success on import")
    conn.close()
