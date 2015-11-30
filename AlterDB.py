import sqlite3 as sql

if __name__ == '__main__':

    conn = sql.connect("bot.db")
    cur = conn.cursor()
    cur.execute("ALTER TABLE bans ADD Channel TEXT")
    conn.commit()
