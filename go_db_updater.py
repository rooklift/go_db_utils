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
                    dyer text,
                    SZ int,
                    HA int,
                    PB text,
                    PW text,
                    RE text,
                    DT text,
                    EV text);
        ''')
except:
    pass

# Make a set of all files in the database...

print("Noting all files in database")

db_known_files = set()

c.execute(
    '''
            SELECT path from Games;
    '''
)

for row in c:
    db_known_files.add(row[0])

# Make a set of all files in the directory structure...

print("Noting all files in the directories.", end="")

count = 0

dir_known_files = set()

for rootdir in rootdirs:
    for root, dirs, files in os.walk(rootdir):
        for f in files:
            path = os.path.join(root, f)
            dir_known_files.add(path)
            count += 1
            if count % 10000 == 0:
                print(".", end="")
                sys.stdout.flush()

print()

# Subtract...

files_to_add_to_db = dir_known_files - db_known_files

files_to_add_list = list(files_to_add_to_db)
files_to_add_list.sort()

# Add them to db...

print("Updating database")

count = 0

for path in files_to_add_list:
    try:
        sgfroot = gofish.load(path)
        filename = os.path.basename(path)
    except:
        continue

    # The Dyer signature is an almost-unique signature per game. Note to self: to retrieve apparent duplicate games from the database, use:
    # '''select filename, dyer, PB, PW from Games where dyer in (select dyer from Games group by dyer having count(*) >1) order by dyer;'''

    dyer = sgfroot.dyer()

    try:
        SZ = int(sgfroot.properties["SZ"][0])
    except:
        SZ = 19

    try:
        HA = int(sgfroot.properties["HA"][0])
    except:
        HA = 0

    try:
        PB = sgfroot.properties["PB"][0].strip()
    except:
        PB = ""

    try:
        PW = sgfroot.properties["PW"][0].strip()
    except:
        PW = ""

    try:
        RE = sgfroot.properties["RE"][0].strip()
    except:
        RE = ""

    try:
        DT = sgfroot.properties["DT"][0].strip()
    except:
        DT = ""

    try:
        EV = sgfroot.properties["EV"][0].strip()
    except:
        EV = ""

    fields = (path, filename, dyer, SZ, HA, PB, PW, RE, DT, EV)
    command = '''
                 INSERT INTO Games(path, filename, dyer, SZ, HA, PB, PW, RE, DT, EV)
                 VALUES(?,?,?,?,?,?,?,?,?,?);
              '''

    c.execute(command, fields)

    print(filename)
    count += 1

conn.commit()
c.close()

print("{} files added to database".format(count))
print("Database size now: {}".format(len(db_known_files) + len(files_to_add_to_db)))
input()
