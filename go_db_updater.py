import os, sqlite3, sys
import gofish       # https://github.com/fohristiwhirl/gofish

rootdirs = ["GoGoD", "Go4Go"]

conn = sqlite3.connect('go.db')
c = conn.cursor()

# Create table if needed...

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
    pass

# Make a set of all files in the database...

print("Noting all files in database...")

db_known_files = set()

c.execute(
    '''
            SELECT path from Games
    '''
)

for row in c:
    db_known_files.add(row[0])

# Make a set of all files in the directory structure...

print("Noting all files in the directories...")

dir_known_files = set()

for rootdir in rootdirs:
    for root, dirs, files in os.walk(rootdir):
        for f in files:
            path = os.path.join(root, f)
            dir_known_files.add(path)

# Subtract...

files_to_add_to_db = dir_known_files - db_known_files

# Add them to db...

print("Updating database...")

count = 0

for path in files_to_add_to_db:
    try:
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
    count += 1

conn.commit()
c.close()

print("{} files added to database...".format(count))
input()
