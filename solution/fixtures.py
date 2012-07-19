# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import errno
import io
import os
import shutil
import sys

from .serializers import json, to_unicode


FIXTURES_PATH = 'fixtures'
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def make_dirs(path):
    try:
        os.makedirs(path)
    except (OSError), e:
        if e.errno != errno.EEXIST:
            raise
    return path


def dump_data(db, models, fixtures_path):
    make_dirs(fixtures_path)
    for m in models:
        filepath = os.path.join(fixtures_path, '%s.json' % m.__name__.lower())
        print 'Saving %s' % filepath
        with io.open(filepath, 'w+t', encoding='utf-8') as f:
            f.write(to_unicode(db.query(m).to_json()))


def load_data(db, models, fixtures_path):
    for m in models:
        filepath = os.path.join(fixtures_path, '%s.json' % m.__name__.lower())
        if not os.path.isfile(filepath):
            continue
        print 'Loading %s' % filepath
        with io.open(filepath, 'r+t', encoding='utf-8') as f:
            data = json.loads(f.read())

        ids = frozenset([r.id for r in db.query(m.id)])
        columns = m.__table__.columns
        date_fields = [c.name for c in columns
            if isinstance(c.type, db.Date)]
        datetime_fields = [c.name for c in columns
            if isinstance(c.type, db.DateTime)]

        for row in data:
            row_id = row.get('id')
            if row_id and row_id in ids:
                continue

            for name in date_fields:
                if name not in row:
                    continue
                row[name] = datetime.datetime.strptime(row[name], DATE_FORMAT).date()

            for name in datetime_fields:
                if name not in row:
                    continue
                row[name] = datetime.datetime.strptime(row[name], DATETIME_FORMAT)
            
            sys.stdout.write('.')
            db.add(m(**row))
        print ''


def load_media(fixtures_path):
    def copy_file(dst):
        src = os.path.join(fixtures_path, dst)
        dst_dir = os.path.dirname(dst)
        make_dirs(dst_dir)
        shutil.copy(src, dst)

    for folder, subs, files in os.walk(fixtures_path):
        if folder == fixtures_path:
            continue
        ffolder = os.path.relpath(folder, fixtures_path)
        for filename in files:
            if filename.startswith('.'):
                continue
            relpath = os.path.join(ffolder, filename) \
                .lstrip('.').lstrip('/')
            copy_file(relpath)

