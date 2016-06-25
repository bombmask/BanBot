import twitchtools

def getargs():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("--debug", 				default=False, 			help="Use Debug Mode", 			action="store_true"	)
	parser.add_argument("--cfgfile",			default="config/cfg.json", 	help="Specify the configuration file", type=str )
	parser.add_argument('-c','--channels', nargs='+', help='List of channels to join on startup')

	return parser.parse_args()

def config(filename=None):
	import json
	if filename == None:
		filename = getargs().cfgfile
	
	with open(filename) as fin:
		cfg = json.load(fin)

	return cfg

def main():
	args = getargs()
	cfg = config()



if __name__ == '__main__':
	main()