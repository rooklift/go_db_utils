import os, re, sqlite3, subprocess, tkinter

PROGRAM = "C:\\Programs (self-installed)\\Sabaki\\sabaki.exe"
DBFILE = "go.db"

class Game():
    def __init__(self, path, filename, PW, PB, RE, HA, EV, DT):
        self.path = path
        self.filename = filename
        self.PW = PW
        self.PB = PB
        self.RE = RE
        self.HA = HA
        self.EV = EV
        self.DT = DT

    @property
    def date(self):
        date = ""
        if self.DT != None:
            try:
                date = re.search('''.?(\d\d\d\d-\d\d-\d\d).?''', self.DT).group(1)
            except:
                try:
                    date = re.search('''.?(\d\d\d\d-\d\d).?''', self.DT).group(1)
                except:
                    try:
                        date = re.search('''.?(\d\d\d\d).?''', self.DT).group(1)
                    except:
                        pass
        return date

    @property
    def description(self):

        direction = " ? "
        result = ""
        if self.RE != None:

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

        if self.HA != None:
            handicap = "(H{})".format(self.HA)
        else:
            handicap = ""

        if self.PW != None:
            PW = self.PW
        else:
            PW = ""

        if self.PB != None:
            PB = self.PB
        else:
            PB = ""

        if self.EV != None:
            event = self.EV
        else:
            event = ""

        return "{:10}   {:7} {:24} {} {:24}  {:5} {} ".format(self.date[0:10], result[0:7], PW[0:24], direction, PB[0:24], handicap, event)

def launcher(gameslist):
    sel = listbox.curselection()
    if sel:
        path = gameslist[sel[0]].path
        subprocess.Popen([PROGRAM, path])

def searcher(gameslist):
    gameslist[:] = []       # Clear the list in place so other references to it are affected

    p1 = p1_box.get().strip()
    p2 = p2_box.get().strip()

    listbox.delete(0, tkinter.END)

    if not p1 and not p2:
        result_count.config(text = "")
        return

    if p1 and not p2:
        search_one(p1, gameslist)
    elif p2 and not p1:
        search_one(p2, gameslist)
    else:
        search_two(p1, p2, gameslist)

    s = "{} games found".format(len(gameslist))

    result_count.config(text = s)

def search_one(name, gameslist):
    name = "%" + name + "%"

    c.execute('''SELECT path, filename, PW, PB, RE, HA, EV, DT
                 FROM Games
                 WHERE (PB like ? or PW like ?) and (SZ = 19 or SZ = NULL)
                 ORDER BY DT;''',
             (name, name))

    for row in c:
        game = Game(path = row[0], filename = row[1], PW = row[2], PB = row[3], RE = row[4], HA = row[5], EV = row[6], DT = row[7])
        gameslist.append(game)

    gameslist.sort(key = lambda x : x.date)

    for game in gameslist:
        listbox.insert(tkinter.END, game.description)

def search_two(name1, name2, gameslist):
    name1 = "%" + name1 + "%"
    name2 = "%" + name2 + "%"

    c.execute('''SELECT path, filename, PW, PB, RE, HA, EV, DT
                 FROM Games
                 WHERE ((PB like ? and PW like ?) or (PB like ? and PW like ?)) and (SZ = 19 or SZ = NULL)
                 ORDER BY DT;''',
             (name1, name2, name2, name1))

    for row in c:
        game = Game(path = row[0], filename = row[1], PW = row[2], PB = row[3], RE = row[4], HA = row[5], EV = row[6], DT = row[7])
        gameslist.append(game)

    gameslist.sort(key = lambda x : x.date)

    for game in gameslist:
        listbox.insert(tkinter.END, game.description)

def selection_poll(gameslist):
    sel = listbox.curselection()
    if sel:
        selected_file.config(text = gameslist[sel[0]].path)
    master.after(100, lambda : selection_poll(gameslist))

# -----------------------------------------------------------

gameslist = list()

conn = sqlite3.connect(DBFILE)
c = conn.cursor()

master = tkinter.Tk()
mainframe = tkinter.Frame(master, borderwidth = 24)

p1_frame = tkinter.Frame(mainframe)
tkinter.Label(p1_frame, text = "Player 1").pack(side = tkinter.LEFT)
p1_box = tkinter.Entry(p1_frame, width = 60)
p1_box.pack(side = tkinter.RIGHT)
p1_frame.pack()

p2_frame = tkinter.Frame(mainframe)
tkinter.Label(p2_frame, text = "Player 2").pack(side = tkinter.LEFT)
p2_box = tkinter.Entry(p2_frame, width = 60)
p2_box.pack(side = tkinter.RIGHT)
p2_frame.pack()

tkinter.Label(mainframe, text = "").pack()
tkinter.Button(mainframe, text = "Search", command = lambda : searcher(gameslist)).pack()
tkinter.Label(mainframe, text = "").pack()

result_count = tkinter.Label(mainframe, text = "")
result_count.pack()
tkinter.Label(mainframe, text = "").pack()

listframe = tkinter.Frame(mainframe)
scrollbar = tkinter.Scrollbar(listframe, orient = tkinter.VERTICAL)
listbox = tkinter.Listbox(listframe, yscrollcommand = scrollbar.set, width = 120, height = 20, font = "Courier")
scrollbar.config(command = listbox.yview)
scrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
listbox.pack(side = tkinter.LEFT, fill = tkinter.BOTH, expand = 1)
listframe.pack()

selected_file = tkinter.Label(mainframe, text = "")
selected_file.pack()
tkinter.Button(mainframe, text = "Launch", command = lambda : launcher(gameslist)).pack()

mainframe.pack()
master.wm_title("Go DB Searcher")

listbox.bind("<Double-Button-1>", lambda x : launcher(gameslist))

selection_poll(gameslist)
tkinter.mainloop()
