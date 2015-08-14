from ...twitchtools import utils



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
		newChannel = message.message.split(" ")[1]

		channel.ircParent.join(newChannel)
		print("Joined :", newChannel)
