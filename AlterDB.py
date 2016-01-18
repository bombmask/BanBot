import datetime
import sqlite3 as sql

if __name__ == '__main__':

    conn = sql.connect("config/bot.db")
    cur = conn.cursor()
    #cur.execute("ALTER TABLE bans ALTER COLUMN Time DATE")
    cur.execute("SELECT * FROM bans")
    bansData = cur.fetchall()
    cur.execute("DROP TABLE bans")
    cur.execute("CREATE TABLE bans ({})".format("Time DATE, User TEXT, Us BOOL DEFAULT true, Channel TEXT DEFAULT undefined"))

    # for i in range(len(bansData)):
    #     bansData[i][0] = (datetime.datetime.strptime('%Y-%m-%d %H:%M:%S.%f', bansData[i][0]))

    cur.executemany("INSERT INTO bans VALUES (?,?,?,?)", bansData)


    conn.commit()
