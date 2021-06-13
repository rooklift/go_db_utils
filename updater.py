#!/usr/bin/env python3

import os, posixpath, sqlite3, sys
import gofish, go_db


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
        full_path = posixpath.join(row[0], row[1])                              # Always use / separators
        db_known_files.add(full_path)

    print(" done")

    # Make a set of all files in the directory structure...

    print("Noting all files in the directories.", end="")
    sys.stdout.flush()

    count = 0

    dir_known_files = set()

    for rootdir in rootdirs:
        for root, dirs, files in os.walk(rootdir):
            for f in files:

                full_path = posixpath.join(root.replace("\\", "/"), f)          # Always use / separators
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

    for full_path in files_to_add_list:
        try:
            sgfroot = gofish.load_sgf_mainline(full_path)
        except:
            continue

        new_record = go_db.record_from_sgf(sgfroot, full_path)
        go_db.add_game_to_db(new_record, full_path, c)

        try:
            s = "  {}".format(os.path.basename(full_path))
            print(s)
        except:
            print("  <unprintable>")
        files_added += 1

    print("{} files added to database".format(files_added))

    # Remove any missing files...

    files_to_del_from_db = db_known_files - dir_known_files

    files_removed = 0

    print("Removing from database")

    for full_path in files_to_del_from_db:
        go_db.delete_game_from_db(full_path, c)
        try:
            s = "  {}".format(os.path.basename(full_path))
            print(s)
        except:
            print("  <unprintable>")
        files_removed += 1

    print("{} files removed from database".format(files_removed))

    # ---------------------------------------------------------------------------------

    conn.commit()
    c.close()

    print("Database size now: {}".format(len(db_known_files) + files_added - files_removed))
    input()


if __name__ == "__main__":
    main()
