import os, sqlite3
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
                    PB text NULL,
                    PW text NULL,
                    RE text NULL,
                    DT text NULL,
                    HA text NULL);
        ''')
except:
    pass

for root, dirs, files in os.walk(rootdir):
    for f in files:
        try:
            path = os.path.join(root, f)
            sgfroot = gofish.load(path)
            filename = os.path.basename(path)
        except:
            continue

        try:
            PB = sgfroot.properties["PB"][0]
        except:
            PB = "NULL"

        try:
            PW = sgfroot.properties["PW"][0]
        except:
            PW = "NULL"

        try:
            RE = sgfroot.properties["RE"][0]
        except:
            RE = "NULL"

        try:
            DT = sgfroot.properties["DT"][0]
        except:
            DT = "NULL"

        try:
            HA = sgfroot.properties["HA"][0]
        except:
            HA = "NULL"

        fields = (path, filename, PB, PW, RE, DT, HA)

        command = '''
                     INSERT INTO Games(path, filename, PB, PW, RE, DT, HA)
                     VALUES(?,?,?,?,?,?,?);
                  '''

        c.execute(command, fields)

        print(filename)

conn.commit()
c.close()
