import logging
import transaction

from ttfrog.db.manager import db
from ttfrog.db import schema

from sqlalchemy.exc import IntegrityError

# move this to json or whatever
data = {
    'Ancestry':  [
        {'id': 1, 'name': 'human'},
        {'id': 2, 'name': 'dragonborn'},
        {'id': 3, 'name': 'tiefling'},
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
            with transaction.manager as tx:
                obj = model(**rec)
                db.session.add(obj)
                obj.slug = db.slugify(rec)
                try:
                    tx.commit()
                except IntegrityError as e:
                    tx.abort()
                    if 'UNIQUE constraint failed' in str(e):
                        logging.info(f"Skipping existing {table} {rec}")
                        continue
                    raise
            logging.info(f"Created {table} {rec}")
