import os, re

class Record():
	def __init__(self, *, path, filename, dyer, PB, PW, BR, WR, RE, HA, EV, DT, SZ):
		self.path = path.replace("\\", "/")
		self.filename = filename
		self.dyer = dyer
		self.PB = PB
		self.PW = PW
		self.BR = BR
		self.WR = WR
		self.RE = RE
		self.HA = HA
		self.EV = EV
		self.DT = DT
		self.SZ = SZ

	@property
	def canonical_date(self):
		canonical_date = ""
		if self.DT:
			try:
				canonical_date = re.search('''.?(\d\d\d\d-\d\d-\d\d).?''', self.DT).group(1)
			except:
				try:
					canonical_date = re.search('''.?(\d\d\d\d-\d\d).?''', self.DT).group(1)
				except:
					try:
						canonical_date = re.search('''.?(\d\d\d\d).?''', self.DT).group(1)
					except:
						try:
							canonical_date = "0" + re.search('''.?(\d\d\d).?''', self.DT).group(1)
						except:
							pass
		return canonical_date

	@property
	def full_path(self):
		return os.path.join(self.path, self.filename).replace("\\", "/")

	@property
	def description(self):

		direction = " ? "
		result = ""
		if self.RE:

			if "B+" in self.RE:
				direction = " > "
			elif "W+" in self.RE:
				direction = " < "

			if "B+R" in self.RE:
				result = "B+R"
			elif "B+T" in self.RE:
				result = "B+T"
			elif "W+R" in self.RE:
				result = "W+R"
			elif "W+T" in self.RE:
				result = "W+T"
			elif "B+" in self.RE:
				result = self.RE.split()[0]     # Some GoGoD results say "B+4 (moves after 150 not known)" or suchlike
				if "B+" not in result:
					result = "B+"
			elif "W+" in self.RE:
				result = self.RE.split()[0]
				if "W+" not in result:
					result = "W+"

		handicap = "(H{})".format(self.HA) if self.HA else ""

		PW = self.PW if self.PW else "?"
		if self.WR:
			PW += " " + self.WR

		PB = self.PB if self.PB else "?"
		if self.BR:
			PB += " " + self.BR

		event = self.EV if self.EV else ""

		return "{:10}   {:7} {:24} {} {:24}  {:5} {} ".format(self.canonical_date[0:10], result[0:7], PB[0:24], direction, PW[0:24], handicap, event)


def record_from_sgf(sgfroot, full_path):

	properties = dict()

	# The Dyer signature is an almost-unique signature per game. Note to self: to retrieve apparent duplicate games from the database, use:
	# '''select filename, dyer, PB, PW from Games where dyer in (select dyer from Games group by dyer having count(*) >1) order by dyer;'''

	properties["dyer"] = sgfroot.dyer()

	try:
		properties["SZ"] = int(sgfroot.props["SZ"][0])
	except:
		properties["SZ"] = 19

	try:
		properties["HA"] = int(sgfroot.props["HA"][0])
	except:
		properties["HA"] = 0

	try:
		properties["PB"] = sgfroot.props["PB"][0].strip()
	except:
		properties["PB"] = ""

	try:
		properties["PW"] = sgfroot.props["PW"][0].strip()
	except:
		properties["PW"] = ""

	try:
		properties["BR"] = sgfroot.props["BR"][0].strip()
	except:
		properties["BR"] = ""

	try:
		properties["WR"] = sgfroot.props["WR"][0].strip()
	except:
		properties["WR"] = ""

	try:
		properties["RE"] = sgfroot.props["RE"][0].strip()
	except:
		properties["RE"] = ""

	try:
		properties["DT"] = sgfroot.props["DT"][0].strip()
	except:
		properties["DT"] = ""

	try:
		properties["EV"] = sgfroot.props["EV"][0].strip()
	except:
		properties["EV"] = ""

	properties["path"] = os.path.dirname(full_path).replace("\\", "/")
	properties["filename"] = os.path.basename(full_path)

	return Record(**properties)


def add_game_to_db(game, cursor):

	command = '''
				INSERT INTO Games(path, filename, dyer, SZ, HA, PB, PW, BR, WR, RE, DT, EV)
				VALUES(?,?,?,?,?,?,?,?,?,?,?,?);
			  '''
	fields = (game.path, game.filename, game.dyer, game.SZ, game.HA, game.PB, game.PW, game.BR, game.WR, game.RE, game.DT, game.EV)
	cursor.execute(command, fields)


def delete_game_from_db(full_path, cursor):

	path, filename = os.path.split(full_path)
	path = path.replace("\\", "/")

	command = '''
				DELETE FROM Games
				WHERE path = ? and filename = ?
			  '''
	fields = (path, filename)
	cursor.execute(command, fields)
