import os, re

class Record():
    def __init__(self, *, path, filename, dyer, PW, PB, RE, HA, EV, DT, SZ):
        self.path = path
        self.filename = filename
        self.dyer = dyer
        self.PW = PW
        self.PB = PB
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

    @property               # This is not the absolute path, but is the "full" path in the sense of including the filename
    def full_path(self):
        return os.path.join(self.path, self.filename)

    @property
    def description(self):

        direction = " ? "
        result = ""
        if self.RE:

            if "B+" in self.RE:
                direction = " < "
            elif "W+" in self.RE:
                direction = " > "

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

        if self.HA:
            handicap = "(H{})".format(self.HA)
        else:
            handicap = ""

        if self.PW:
            PW = self.PW
        else:
            PW = ""

        if self.PB:
            PB = self.PB
        else:
            PB = ""

        if self.EV:
            event = self.EV
        else:
            event = ""

        return "{:10}   {:7} {:24} {} {:24}  {:5} {} ".format(self.canonical_date[0:10], result[0:7], PW[0:24], direction, PB[0:24], handicap, event)


def record_from_sgf(sgfroot, full_path):

    properties = dict()

    # The Dyer signature is an almost-unique signature per game. Note to self: to retrieve apparent duplicate games from the database, use:
    # '''select filename, dyer, PB, PW from Games where dyer in (select dyer from Games group by dyer having count(*) >1) order by dyer;'''

    properties["dyer"] = sgfroot.dyer()

    try:
        properties["SZ"] = int(sgfroot.properties["SZ"][0])
    except:
        properties["SZ"] = 19

    try:
        properties["HA"] = int(sgfroot.properties["HA"][0])
    except:
        properties["HA"] = 0

    try:
        properties["PB"] = sgfroot.properties["PB"][0].strip()
    except:
        properties["PB"] = ""

    try:
        properties["PW"] = sgfroot.properties["PW"][0].strip()
    except:
        properties["PW"] = ""

    try:
        properties["RE"] = sgfroot.properties["RE"][0].strip()
    except:
        properties["RE"] = ""

    try:
        properties["DT"] = sgfroot.properties["DT"][0].strip()
    except:
        properties["DT"] = ""

    try:
        properties["EV"] = sgfroot.properties["EV"][0].strip()
    except:
        properties["EV"] = ""

    path, filename = os.path.split(full_path)
    return Record(path = path, filename = filename, **properties)


def add_game_to_db(game, full_path, cursor):

    path, filename = os.path.split(full_path)

    command = '''
                INSERT INTO Games(path, filename, dyer, SZ, HA, PB, PW, RE, DT, EV)
                VALUES(?,?,?,?,?,?,?,?,?,?);
              '''
    fields = (path, filename, game.dyer, game.SZ, game.HA, game.PB, game.PW, game.RE, game.DT, game.EV)
    cursor.execute(command, fields)


def delete_game_from_db(full_path, cursor):
    
    path, filename = os.path.split(full_path)

    command = '''
                DELETE FROM Games
                WHERE path = ? and filename = ?
              '''
    fields = (path, filename)
    cursor.execute(command, fields)
