#!/usr/bin/env python3

from argparse import ArgumentParser
import sqlite3
from pathlib import Path


def main():
    parser = ArgumentParser()
    parser.add_argument("db_path", type=Path)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db_path)

    all_tags = conn.execute("SELECT name FROM tag").fetchall()
    all_tags = {name[0]: i for i, name in enumerate(all_tags)}

    tags_by_seal = conn.execute("""SELECT seal.id, group_concat(name, ";")
            FROM seal
            JOIN seal_has_tag ON seal.id = seal_has_tag.seal_id
            JOIN tag ON tag.id = seal_has_tag.tag_id
            GROUP BY seal.id""").fetchall()
    tags_by_seal = [{"id": id,
                     "tags": [1 if tag in tags else 0 for tag in all_tags]}
                    for id, tags in tags_by_seal]

    for thing in tags_by_seal:
        print(thing)


if __name__ == "__main__":
    main()
