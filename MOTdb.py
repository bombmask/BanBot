import sqlalchemy, json
from sqlalchemy import create_engine

engine = None
con = None

def Start(url):
	global con
	global engine

	if con == None:

		engine = create_engine(url)
		con = engine.connect()


def Stop():
	global con
	global engine

	if con != None:
		con.close()
		engine.dispose()
		con = None