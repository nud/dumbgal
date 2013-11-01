#!/usr/bin/python3
# -*- coding: utf-8 -*- ex:set ts=4 sw=4:

import sqlite3

class TagStore(object):
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.init_schema()

    def init_schema(self):
        cur = self.conn.cursor()
        cur.execute('PRAGMA user_version')
        if cur.fetchone()[0] < 1:
            cur.execute('CREATE TABLE images (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT UNIQUE, width INTEGER, height INTEGER)')
            cur.execute('CREATE TABLE tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)')
            cur.execute('CREATE TABLE image_tags (image_id INTEGER, tag_id INTEGER, UNIQUE (image_id, tag_id))')
            cur.execute('PRAGMA user_version = 1')
            self.conn.commit()
            cur.close()

    def _query(self, query, args=()):
        cur = self.conn.cursor()
        cur.execute(query, args)
        for row in cur:
            yield row
        cur.close()

    def list_all_images(self):
        return [row[0] for row in self._query("SELECT filename FROM images ORDER BY filename")]

    def list_all_tags(self):
        return [row[0] for row in self._query("SELECT name FROM tags ORDER BY name")]

    def list_images_for_tag(self, tag):
        results = self._query("""SELECT i.filename
                              FROM images i
                              LEFT JOIN image_tags a ON i.id = a.image_id
                              LEFT JOIN tags t ON t.id = a.tag_id
                              WHERE t.name = ?
                              ORDER BY i.filename""", (tag,))
        return [row[0] for row in results]

    def list_tags_for_image(self, filename):
        results = self._query("""SELECT t.name
                              FROM tags t
                              LEFT JOIN image_tags a ON t.id = a.tag_id
                              LEFT JOIN images i ON i.id = a.image_id
                              WHERE i.filename = ?
                              ORDER BY t.name""", (filename,))
        return [row[0] for row in results]

    def add_image(self, filename, width, height):
        cur = self.conn.cursor()
        cur.execute('INSERT OR IGNORE INTO images (filename, width, height) VALUES (?, ?, ?)', (filename, width, height))
        self.conn.commit()
        cur.close()

    def add_tag(self, filename, tag):
        cur = self.conn.cursor()

        cur.execute('SELECT id FROM images WHERE filename=?', (filename,))
        row = cur.fetchone()
        if row is None:
            raise Exception('Image %s does not exist.' % filename)
        image_id = row[0]

        cur.execute('SELECT id FROM tags WHERE name=?', (tag,))
        row = cur.fetchone()
        if row is not None:
            tag_id = row[0]
        else:
            cur.execute('INSERT INTO tags (name) VALUES (?)', (tag,))
            tag_id = cur.lastrowid

        cur.execute('INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES (?, ?)', (image_id, tag_id))
        self.conn.commit()
        cur.close()

    def close(self):
        self.conn.close()
