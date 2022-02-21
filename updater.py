#!/usr/bin/env python3

import json, os, sqlite3, sys
import gofish2, go_db


with open("gogod_name_fixes.json") as infile:
	gogod_name_fixes = json.loads(infile.read())


def fix_root(root):

	PB = root.get("PB")
	if PB and PB in gogod_name_fixes:
		root.set("PB", gogod_name_fixes[PB])
		print("    ", PB, "-->", gogod_name_fixes[PB])

	PW = root.get("PW")
	if PW and PW in gogod_name_fixes:
		root.set("PW", gogod_name_fixes[PW])
		print("    ", PW, "-->", gogod_name_fixes[PW])


def main():

    rootdirs = ["archive"]

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
                        BR text,
                        WR text,
                        RE text,
                        DT text,
                        EV text);
            ''')
    except:
        pass

    # Make a set of all files in the database...

    print("Noting all files in database...", end="")
    sys.stdout.flush()

    db_known_files = set()

    c.execute(
        '''
                SELECT path, filename from Games;
        '''
    )
    print(" SQL query complete, making set...", end="")
    sys.stdout.flush()

    for row in c:
        full_path = os.path.join(row[0], row[1]).replace("\\", "/")
        db_known_files.add(full_path)

    print(" done")

    # Make a set of all files in the directory structure...

    print("Noting all files in the directories.", end="")
    sys.stdout.flush()

    count = 0

    dir_known_files = set()

    for rootdir in rootdirs:
        for dirpath, dirnames, filenames in os.walk(rootdir):
            for f in filenames:
                full_path = os.path.abspath(os.path.join(dirpath, f)).replace("\\", "/")
                dir_known_files.add(full_path)
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

    print("Adding to database")

    files_added = 0
    fail_list = []

    for full_path in files_to_add_list:
        try:
            sgfroot = gofish2.load(full_path)[0]
            if "gogod" in full_path.lower():
            	fix_root(sgfroot)

        except:
            fail_list.append(full_path)
            continue

        new_record = go_db.record_from_sgf(sgfroot, full_path)
        go_db.add_game_to_db(new_record, c)

        try:
            s = "  {}".format(os.path.basename(full_path))
            print(s)
        except:
            print("  <unprintable>")
        files_added += 1

    print("{} files added to database".format(files_added))

    # Remove any missing files...

    files_to_del_from_db = db_known_files - dir_known_files
    files_to_del_list = list(files_to_del_from_db)
    files_to_del_list.sort()

    files_removed = 0

    print("Removing from database")

    for full_path in files_to_del_list:
        go_db.delete_game_from_db(full_path, c)
        try:
            s = "  {}".format(os.path.basename(full_path))
            print(s)
        except:
            print("  <unprintable>")
        files_removed += 1

    print("{} files removed from database".format(files_removed))

    # Note any files we failed to add...

    if len(fail_list) > 0:
        fail_list.sort()
        print("The following files could not be added, due to errors")
        for full_path in fail_list:
            try:
                s = "  {}".format(os.path.basename(full_path))
                print(s)
            except:
                print("  <unprintable>")


    # ---------------------------------------------------------------------------------

    conn.commit()
    c.close()

    print("Database size now: {}".format(len(db_known_files) + files_added - files_removed))
    input()


if __name__ == "__main__":
    main()

