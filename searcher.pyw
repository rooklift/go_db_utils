import os, sqlite3, subprocess, tkinter

PROGRAM = "C:\\Programs (self-installed)\\Sabaki\\sabaki.exe"
DBFILE = "gogod.db"

class Game():
    def __init__(self, path, filename, PW, PB, RE, HA, EV):
        self.path = path
        self.filename = filename
        self.PW = PW
        self.PB = PB
        self.RE = RE
        self.HA = HA
        self.EV = EV

    @property
    def description(self):

        if "B+" in self.RE:
            direction = " < "
        elif "W+" in self.RE:
            direction = " > "
        else:
            direction = " ? "

        if str(self.HA) != "NULL":
            handicap = "(H{})".format(self.HA)
        else:
            handicap = ""

        if str(self.EV) != "NULL":
            event = self.EV
        else:
            event = ""

        return "{:10}   {:24} {} {:24}  {:5} {} ".format(self.filename[0:10], self.PW[0:24], direction, self.PB[0:24], handicap, event)

def launcher():
    sel = listbox.curselection()
    if sel:
        path = games[sel[0]].path
        subprocess.Popen([PROGRAM, path])

def searcher():
    global p1_box
    global p2_box
    global games

    p1 = p1_box.get().strip()
    p2 = p2_box.get().strip()

    listbox.delete(0, tkinter.END)
    games = dict()

    if not p1 and not p2:
        return

    if p1 and not p2:
        search_one(p1)
    elif p2 and not p1:
        search_one(p2)
    else:
        search_two(p1, p2)

def search_one(name):
    name = "%" + name + "%"

    c.execute('''SELECT path, filename, PW, PB, RE, HA, EV from Games where PB like ? or PW like ?;''', (name, name))

    for n, row in enumerate(c):
        game = Game(path = row[0], filename = row[1], PW = row[2], PB = row[3], RE = row[4], HA = row[5], EV = row[6])
        listbox.insert(tkinter.END, game.description)
        games[n] = game

def search_two(name1, name2):
    name1 = "%" + name1 + "%"
    name2 = "%" + name2 + "%"

    c.execute('''SELECT path, filename, PW, PB, RE, HA, EV from Games where (PB like ? and PW like ?) or (PB like ? and PW like ?);''', (name1, name2, name2, name1))

    for n, row in enumerate(c):
        listbox.insert(tkinter.END, game.description)
        games[n] = game

# -----------------------------------------------------------

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
tkinter.Button(mainframe, text = "Search", command = searcher).pack()
tkinter.Label(mainframe, text = "").pack()

listframe = tkinter.Frame(mainframe)
scrollbar = tkinter.Scrollbar(listframe, orient = tkinter.VERTICAL)
listbox = tkinter.Listbox(listframe, yscrollcommand = scrollbar.set, width = 120, height = 20, font = "Courier")
scrollbar.config(command = listbox.yview)
scrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
listbox.pack(side = tkinter.LEFT, fill = tkinter.BOTH, expand = 1)
listframe.pack()

tkinter.Label(mainframe, text = "").pack()
tkinter.Button(mainframe, text = "Launch", command = launcher).pack()

mainframe.pack()
master.wm_title("GoGoD Searcher")

games = dict()
tkinter.mainloop()
