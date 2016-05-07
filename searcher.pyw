import os, re, sqlite3, subprocess, tkinter

PROGRAM = "C:\\Programs (self-installed)\\Sabaki\\sabaki.exe"
DBFILE = "go.db"

class Game():
    def __init__(self, path, filename, dyer, PW, PB, RE, HA, EV, DT):
        self.path = path
        self.filename = filename
        self.dyer = dyer
        self.PW = PW
        self.PB = PB
        self.RE = RE
        self.HA = HA
        self.EV = EV
        self.DT = DT

    @property
    def date(self):
        date = ""
        if self.DT:
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

        return "{:10}   {:7} {:24} {} {:24}  {:5} {} ".format(self.date[0:10], result[0:7], PW[0:24], direction, PB[0:24], handicap, event)

def launcher(gameslist):
    sel = listbox.curselection()
    if sel:
        subprocess.Popen([PROGRAM, gameslist[sel[0]].full_path])

def searcher(gameslist):
    gameslist[:] = []       # Clear the list in place so other references to it are affected

    p1 = p1_box.get().strip()
    p2 = p2_box.get().strip()
    ev = ev_box.get().strip()
    dt = dt_box.get().strip()

    listbox.delete(0, tkinter.END)

    name1 = "%" + p1 + "%"
    name2 = "%" + p2 + "%"
    event = "%" + ev + "%"
    date = "%" + dt + "%"

    c.execute(  '''
                SELECT
                    path, filename, dyer, PW, PB, RE, HA, EV, DT
                FROM
                    Games
                WHERE
                    ((PB like ? and PW like ?) or (PB like ? and PW like ?))
                and
                    (SZ = 19)
                and
                    (EV like ?)
                and
                    (DT like ?)
                ORDER
                    BY DT
                ;''',
             (name1, name2, name2, name1, event, date))

    for row in c:
        game = Game(path = row[0], filename = row[1], dyer = row[2], PW = row[3], PB = row[4], RE = row[5], HA = row[6], EV = row[7], DT = row[8])
        gameslist.append(game)

    # Sort by Dyer so the deduplicator can look at neighbouring games and compare dates...
    # (the reverse doesn't work, since duplicates might not be next to each other if sorted by date)

    gameslist.sort(key = lambda x : x.dyer)
    deduplicate(gameslist)
    gameslist.sort(key = lambda x : x.date)

    for game in gameslist:
        listbox.insert(tkinter.END, game.description)

    s = "{} games found".format(len(gameslist))
    result_count.config(text = s)
    return

def deduplicate(gameslist):
    for n in range(len(gameslist) - 1, 0, -1):
        if gameslist[n].dyer == gameslist[n - 1].dyer and gameslist[n].date == gameslist[n - 1].date:
            gameslist.pop(n)

def selection_poll(gameslist):
    sel = listbox.curselection()
    if sel:
        selected_file.config(text = gameslist[sel[0]].full_path)
    else:
        selected_file.config(text = "")
    master.after(100, lambda : selection_poll(gameslist))

# -----------------------------------------------------------

gameslist = list()

conn = sqlite3.connect(DBFILE)
c = conn.cursor()

master = tkinter.Tk()
mainframe = tkinter.Frame(master, borderwidth = 24)

p1_frame = tkinter.Frame(mainframe)
tkinter.Label(p1_frame, text = "Player 1 ", font = "Courier").pack(side = tkinter.LEFT)
p1_box = tkinter.Entry(p1_frame, width = 60)
p1_box.pack(side = tkinter.RIGHT)
p1_frame.pack()

p2_frame = tkinter.Frame(mainframe)
tkinter.Label(p2_frame, text = "Player 2 ", font = "Courier").pack(side = tkinter.LEFT)
p2_box = tkinter.Entry(p2_frame, width = 60)
p2_box.pack(side = tkinter.RIGHT)
p2_frame.pack()

ev_frame = tkinter.Frame(mainframe)
tkinter.Label(ev_frame, text = "   Event ", font = "Courier").pack(side = tkinter.LEFT)
ev_box = tkinter.Entry(ev_frame, width = 60)
ev_box.pack(side = tkinter.RIGHT)
ev_frame.pack()

dt_frame = tkinter.Frame(mainframe)
tkinter.Label(dt_frame, text = "    Date ", font = "Courier").pack(side = tkinter.LEFT)
dt_box = tkinter.Entry(dt_frame, width = 60)
dt_box.pack(side = tkinter.RIGHT)
dt_frame.pack()

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
