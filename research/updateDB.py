import sqlalchemy, json
from sqlalchemy import create_engine

print("loading json file...")

with open("outfile.json") as fin:
	cfg = json.load(fin)

print("finished...")
print("Dict size is {}".format(len(cfg)))

print("connecting to DB...")

engine = create_engine("postgres://postgres:mysecretpassword@107.170.251.210:32489/dev")
con = engine.connect()

print("finished...")

idx = 0
interval = len(cfg)//1000

print("Begining Transaction")
for k,v in cfg.items():
	idx += 1
	con.execute("""UPDATE messages SET userid = %s WHERE username LIKE %s""", v, k)
	if idx % interval == 0:
		print('{percent:.2%} -> ID: {idx} -> {user}:{uid}'.format(idx=idx, percent=(idx / len(cfg)), user=k, uid=v))
		



print("Finished...")
print("cleaning up...")

con.close()
engine.dispose()
