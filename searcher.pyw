import os, re, sqlite3, subprocess, tkinter

PROGRAMS =  [
                ("Sabaki", ["C:\\Programs (self-installed)\\Sabaki\\sabaki.exe"]),
                ("Gofish", ["python", "C:\\Users\\Owner\\github\\gofish\\game_editor.pyw"]),
            ]

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


class Root(tkinter.Tk):
    def __init__(self, *args, **kwargs):

        tkinter.Tk.__init__(self, *args, **kwargs)

        self.wm_title("Go DB Searcher")

        # Frames for layout...

        mainframe = tkinter.Frame(self, borderwidth = 24)
        listframe = tkinter.Frame(mainframe)
        p1_frame = tkinter.Frame(mainframe)
        p2_frame = tkinter.Frame(mainframe)
        ev_frame = tkinter.Frame(mainframe)
        dt_frame = tkinter.Frame(mainframe)
        ha_frame = tkinter.Frame(mainframe)
        launch_frame = tkinter.Frame(mainframe)

        # Attributes...

        self.conn = sqlite3.connect(DBFILE)
        self.c = self.conn.cursor()
        self.gameslist = list()
        self.p1_box = tkinter.Entry(p1_frame, width = 60)
        self.p2_box = tkinter.Entry(p2_frame, width = 60)
        self.ev_box = tkinter.Entry(ev_frame, width = 60)
        self.dt_box = tkinter.Entry(dt_frame, width = 60)
        self.ha_box = tkinter.Entry(ha_frame, width = 60)
        self.deduplicate_var = tkinter.IntVar(value = 1)
        self.result_count = tkinter.Label(mainframe, text = "")
        self.scrollbar = tkinter.Scrollbar(listframe, orient = tkinter.VERTICAL)
        self.listbox = tkinter.Listbox(listframe, yscrollcommand = self.scrollbar.set, width = 120, height = 20, font = "Courier")
        self.selected_file = tkinter.Label(mainframe, text = "")

        # Finalise the layout...

        tkinter.Label(p1_frame, text = "Player 1 ", font = "Courier").pack(side = tkinter.LEFT)
        self.p1_box.pack(side = tkinter.RIGHT)
        p1_frame.pack()

        tkinter.Label(p2_frame, text = "Player 2 ", font = "Courier").pack(side = tkinter.LEFT)
        self.p2_box.pack(side = tkinter.RIGHT)
        p2_frame.pack()

        tkinter.Label(ev_frame, text = "   Event ", font = "Courier").pack(side = tkinter.LEFT)
        self.ev_box.pack(side = tkinter.RIGHT)
        ev_frame.pack()

        tkinter.Label(dt_frame, text = "    Date ", font = "Courier").pack(side = tkinter.LEFT)

        self.dt_box.pack(side = tkinter.RIGHT)
        dt_frame.pack()

        tkinter.Label(ha_frame, text = "Handicap ", font = "Courier").pack(side = tkinter.LEFT)

        self.ha_box.pack(side = tkinter.RIGHT)
        ha_frame.pack()

        tkinter.Checkbutton(mainframe, text="Deduplicate", variable = self.deduplicate_var).pack()

        tkinter.Button(mainframe, text = "Search", command = lambda : self.searcher()).pack()
        tkinter.Label(mainframe, text = "").pack()

        self.result_count.pack()

        self.scrollbar.config(command = self.listbox.yview)
        self.scrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
        self.listbox.pack(side = tkinter.LEFT, fill = tkinter.BOTH, expand = 1)
        listframe.pack()

        self.selected_file.pack()

        for n, prog in enumerate(PROGRAMS):
            tkinter.Button(launch_frame, text = "Launch in {}".format(PROGRAMS[n][0]), command = lambda x=n : self.launcher(x)).pack(side=tkinter.LEFT)

        launch_frame.pack()

        # Done...

        mainframe.pack()

        self.listbox.bind("<Double-Button-1>", lambda x : self.launcher(0))

        self.selection_poll()
        tkinter.mainloop()

    def launcher(self, n):
        sel = self.listbox.curselection()
        if sel:
            args = []
            for item in PROGRAMS[n][1]:
                args.append(item)
            relative_path = self.gameslist[sel[0]].full_path
            absolute_path = os.path.abspath(relative_path)
            args.append(absolute_path)
            subprocess.Popen(args)

    def searcher(self):
        self.gameslist[:] = []

        p1 = self.p1_box.get().strip()
        p2 = self.p2_box.get().strip()
        ev = self.ev_box.get().strip()
        dt = self.dt_box.get().strip()
        ha = self.ha_box.get().strip()

        self.listbox.delete(0, tkinter.END)

        name1 = "%" + p1 + "%"
        name2 = "%" + p2 + "%"
        event = "%" + ev + "%"
        date = "%" + dt + "%"

        try:
            ha_min = int(ha)
        except:
            ha_min = 0
            self.ha_box.delete(0, tkinter.END)

        self.c.execute(
                    ''' SELECT
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
                        and
                            (HA >= ?)
                        ORDER
                            BY DT
                    ;''',
                 (name1, name2, name2, name1, event, date, ha_min))

        for row in self.c:
            game = Game(path = row[0], filename = row[1], dyer = row[2], PW = row[3], PB = row[4], RE = row[5], HA = row[6], EV = row[7], DT = row[8])
            self.gameslist.append(game)

        if self.deduplicate_var.get():
            self.deduplicate()
        self.gameslist.sort(key = lambda x : x.date)

        for game in self.gameslist:
            self.listbox.insert(tkinter.END, game.description)

        s = "{} games found".format(len(self.gameslist))
        self.result_count.config(text = s)
        return

    def deduplicate(self):

        # Sort by Dyer so the deduplicator can look at neighbouring games and compare dates...
        # (the reverse doesn't work, since duplicates might not be next to each other if sorted by date)

        self.gameslist.sort(key = lambda x : x.dyer)
        for n in range(len(self.gameslist) - 1, 0, -1):
            if self.gameslist[n].dyer == self.gameslist[n - 1].dyer and self.gameslist[n].date == self.gameslist[n - 1].date:
                self.gameslist.pop(n)

    def selection_poll(self):
        sel = self.listbox.curselection()
        if sel:
            self.selected_file.config(text = self.gameslist[sel[0]].full_path)
        else:
            self.selected_file.config(text = "")
        self.after(100, lambda : self.selection_poll())

if __name__ == "__main__":
    app = Root()
    app.mainloop()
