import logging

from ttfrog.db.manager import db
from ttfrog.db import schema

from sqlalchemy.exc import IntegrityError

# move this to json or whatever
data = {
    'Ancestry':  [
        {'name': 'human'},
        {'name': 'dragonborn'},
        {'name': 'tiefling'},
    ],
    'Character': [
        {'id': 1, 'name': 'Sabetha', 'ancestry': 'tiefling', 'level': 10, 'str': 10, 'dex': 10, 'con': 10, 'int': 10, 'wis': 10, 'cha': 10},
    ]
}


def bootstrap():
    """
    Initialize the database with source data. Idempotent; will skip anything that already exists.
    """
    db.init()
    for table, records in data.items():
        model = getattr(schema, table)

        for rec in records:
            obj = model(**rec)
            try:
                with db.transaction():
                    db.session.add(obj)
                    logging.info(f"Created {table} {obj}")
            except IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    logging.info(f"Skipping existing {table} {obj}")
                    continue
                raise
