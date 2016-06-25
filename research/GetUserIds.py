#! /usr/bin/python3

import datetime, json

class MessageObject(object):
	def __init__(self, mstring):
		mstring = mstring.strip("\r\n") # Double check
		self.raw = mstring
		
		self._tags 		= None #initalize to none
		self._COM 		= None
		self._CParam 	= None
		self._CList 	= None
		self._CPrefix	= None

		self._time = datetime.datetime.now()

		if self.raw[0] == "@":
			tmp = self.raw.split(' ', 1)
			self._tag_string = tmp[0]
			mstring = tmp[1]

		else:
			self._tag_string = False

		self._message_parts 	= 	mstring.split(":", 2)

		# self._tag_string 		=	self._message_parts[0]
		self._command_string 	= 	self._message_parts[1]
		self._message_string 	= 	(self._message_parts[2] if len(self._message_parts) > 2 else "")

	def __str__(self):
		return "Action: {}: {}".format(self.command, self.message)

	@property
	def tags(self):
		if self._tags != None and self._tag_string != False:
			return self._tags

		# Else Parse Tags
		self._tags = {tag.split("=",1)[0]:tag.split("=",1)[1] for tag in self._tag_string[1:].split(";")}

		return self._tags

	@property
	def message(self):
		return self._message_string

	@property
	def prefix(self):
		if self._CPrefix != None:
			return self._CPrefix

		self._CPrefix = self.CList[0]
		return self._CPrefix

	@property
	def command(self):
		if self._COM != None:
			return self._COM
		
		self._COM = self.CList[1]
		return self._COM

	@property
	def commandParams(self):
		if self._CParam != None:
			return self._CParam

		self._CParam = self.CList[2:]
		return self._CParam

	@property
	def CList(self):
		if self._CList != None:
			return self._CList

		self._CList = self._command_string.split(" ")

		return self._CList

import csv
with open("C:\\Users\\Micah\\Desktop\\userrawnew.csv", encoding="utf8") as fin:

	sr = csv.reader(fin, delimiter=",", quotechar="\"")
	for row in sr:
		try:
			print(MessageObject(row[1]).prefix)

			

		except Exception as E:
			pass
