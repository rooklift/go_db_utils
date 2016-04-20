import os, sqlite3, sys
import gofish       # https://github.com/fohristiwhirl/gofish

rootdir = "Database"

conn = sqlite3.connect('gogod.db')
c = conn.cursor()

try:
    c.execute(
        '''
                CREATE TABLE Games (
                    path text,
                    filename text,
                    SZ int NULL,
                    PB text NULL,
                    PW text NULL,
                    RE text NULL,
                    DT text NULL,
                    EV text NULL,
                    HA text NULL);
        ''')
except:
    sys.exit(1)

for root, dirs, files in os.walk(rootdir):
    for f in files:
        try:
            path = os.path.join(root, f)
            sgfroot = gofish.load(path)
            filename = os.path.basename(path)
        except:
            continue

        try:
            SZ = int(sgfroot.properties["SZ"][0])
        except:
            SZ = None

        try:
            PB = sgfroot.properties["PB"][0]
        except:
            PB = None

        try:
            PW = sgfroot.properties["PW"][0]
        except:
            PW = None

        try:
            RE = sgfroot.properties["RE"][0]
        except:
            RE = None

        try:
            DT = sgfroot.properties["DT"][0]
        except:
            DT = None

        try:
            EV = sgfroot.properties["EV"][0]
        except:
            EV = None

        try:
            HA = sgfroot.properties["HA"][0]
        except:
            HA = None

        fields = (path, filename, SZ, PB, PW, RE, DT, EV, HA)
        command = '''
                     INSERT INTO Games(path, filename, SZ, PB, PW, RE, DT, EV, HA)
                     VALUES(?,?,?,?,?,?,?,?,?);
                  '''

        c.execute(command, fields)

        print(filename)

conn.commit()
c.close()
