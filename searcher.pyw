#!/usr/bin/env python3

import os, sqlite3, subprocess, sys, tkinter
import gofish, go_db

PROGRAMS =  [
                ("Ogatak", ["C:\\Programs (self-installed)\\Ogatak\\ogatak.exe"]),
                ("Sabaki", ["C:\\Programs (self-installed)\\Sabaki\\Sabaki.exe"]),
                ("Gofish", ["python", "C:\\Users\\Owner\\github\\gofish\\game_editor.py"]),
            ]

DBFILE = "go.db"


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
        path_frame = tkinter.Frame(mainframe)
        filename_frame = tkinter.Frame(mainframe)
        dyer_frame = tkinter.Frame(mainframe)
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
        self.path_box = tkinter.Entry(path_frame, width = 60)
        self.filename_box = tkinter.Entry(filename_frame, width = 60)
        self.dyer_box = tkinter.Entry(dyer_frame, width = 60)
        self.deduplicate_var = tkinter.IntVar(value = 0)
        self.result_count = tkinter.Label(mainframe, text = "")
        self.scrollbar = tkinter.Scrollbar(listframe, orient = tkinter.VERTICAL)
        self.listbox = tkinter.Listbox(listframe, yscrollcommand = self.scrollbar.set, width = 150, height = 20, font = "Courier")
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

        tkinter.Label(path_frame, text = "    Path ", font = "Courier").pack(side = tkinter.LEFT)
        self.path_box.pack(side = tkinter.RIGHT)
        path_frame.pack()

        tkinter.Label(filename_frame, text = "Filename ", font = "Courier").pack(side = tkinter.LEFT)
        self.filename_box.pack(side = tkinter.RIGHT)
        filename_frame.pack()

        tkinter.Label(dyer_frame, text = "    Dyer ", font = "Courier").pack(side = tkinter.LEFT)
        self.dyer_box.pack(side = tkinter.RIGHT)
        dyer_frame.pack()

        tkinter.Checkbutton(mainframe, text="Deduplicate", variable = self.deduplicate_var).pack()

        tkinter.Button(mainframe, text = "Search", command = lambda : self.searcher()).pack()

        self.result_count.pack()

        self.scrollbar.config(command = self.listbox.yview)
        self.scrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
        self.listbox.pack(side = tkinter.LEFT, fill = tkinter.BOTH, expand = 1)
        listframe.pack()

        self.selected_file.pack()

        tkinter.Button(launch_frame, text = "RE-IMPORT FILE", command = lambda: self.update_file_info()).pack(side=tkinter.LEFT)

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
            args.append(self.gameslist[sel[0]].full_path)
            subprocess.Popen(args)

    def update_file_info(self):

        sel = self.listbox.curselection()

        if sel:

            old_record = self.gameslist[sel[0]]

            try:

                sgfroot = gofish.load(old_record.full_path)
                new_record = go_db.record_from_sgf(sgfroot, old_record.full_path)

                go_db.delete_game_from_db(old_record.full_path, self.c)  # Delete...
                go_db.add_game_to_db(new_record, self.c)                 # Then add it again (we should really update, meh)

                self.gameslist[sel[0]] = new_record

            except (FileNotFoundError, gofish.BadBoardSize, gofish.ParserFail):

                go_db.delete_game_from_db(old_record.full_path, self.c)
                self.gameslist.pop(sel[0])

            self.conn.commit()
            self.refresh_listbox_from_gameslist()

    def refresh_listbox_from_gameslist(self):

        self.listbox.delete(0, tkinter.END)

        for game in self.gameslist:
            self.listbox.insert(tkinter.END, game.description)

        s = "{} games found".format(len(self.gameslist))
        self.result_count.config(text = s)

    def searcher(self):
        p1 = self.p1_box.get().strip()
        p2 = self.p2_box.get().strip()
        ev = self.ev_box.get().strip()
        dt = self.dt_box.get().strip()
        ha = self.ha_box.get().strip()
        path = self.path_box.get().strip()
        filename = self.filename_box.get().strip()
        dyer = self.dyer_box.get().strip()

        p1 = "%" + p1 + "%"
        p2 = "%" + p2 + "%"
        ev = "%" + ev + "%"
        dt = "%" + dt + "%"

        path = "%" + path + "%"
        filename = "%" + filename + "%"
        dyer = "%" + dyer + "%"

        try:
            ha_min = int(ha)
        except:
            ha_min = 0
            self.ha_box.delete(0, tkinter.END)

        self.c.execute(
            '''
            SELECT
                path, filename, dyer, PB, PW, BR, WR, RE, HA, EV, DT, SZ
            FROM
                Games
            WHERE
                (
                    (PB like ? and PW like ?) or (PB like ? and PW like ?)
                ) and (
                    SZ = 19
                ) and (
                    EV like ?
                ) and (
                    DT like ?
                ) and (
                    HA >= ?
                ) and (
                    path like ?
                ) and (
                    filename like ?
                ) and (
                    dyer like ?
                )
            ''',
            (p1, p2, p2, p1, ev, dt, ha_min, path, filename, dyer)
        )

        self.gameslist[:] = []

        for row in self.c:
            game = go_db.Record(path = row[0], filename = row[1], dyer = row[2], PB = row[3], PW = row[4], BR = row[5], WR = row[6],
                                RE = row[7], HA = row[8], EV = row[9], DT = row[10], SZ = row[11])
            self.gameslist.append(game)

        if self.deduplicate_var.get():
            self.deduplicate()
        self.gameslist.sort(key = lambda x : [x.canonical_date, x.EV, x.filename])

        self.refresh_listbox_from_gameslist()

        return

    def deduplicate(self):

        # Sort by Dyer so the deduplicator can look at neighbouring games and compare dates...
        # (the reverse doesn't work, since duplicates might not be next to each other if sorted by date)

        self.gameslist.sort(key = lambda x : x.dyer)
        for n in range(len(self.gameslist) - 1, 0, -1):
            if self.gameslist[n].dyer == self.gameslist[n - 1].dyer and self.gameslist[n].canonical_date == self.gameslist[n - 1].canonical_date:
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
