import base64
import hashlib
import logging

from ttfrog.db import db, session


# move this to json or whatever
data = {
    'ancestry':  [
        {'name': 'human'},
        {'name': 'dragonborn'},
    ],
}


def slug_from_rec(rec):
    """
    Create a uniquish slug from a dictionary.
    """
    sha1bytes = hashlib.sha1(str(rec).encode())
    return '-'.join([
        base64.urlsafe_b64encode(sha1bytes.digest()).decode("ascii")[:10],
        rec.get('name', '')  # will need to normalize this for URLs
    ])


def bootstrap():
    """
    Initialize the database with source data. Idempotent; will skip anything that already exists.
    """
    db.init_model()
    for table_name, table in db.tables.items():
        if table_name not in data:
            logging.debug("No bootstrap data for table {table_name}; skipping.")
            continue
        for rec in data[table_name]:
            if 'slug' in table.columns:
                rec['slug'] = slug_from_rec(rec)
            stmt = table.insert().values(**rec).prefix_with("OR IGNORE")
            result = session.execute(stmt)
            session.commit()
            last_id = result.inserted_primary_key[0]
            if last_id == 0:
                logging.info(f"Skipped existing {table_name} {rec}")
            else:
                logging.info(f"Created {table_name} {result.inserted_primary_key[0]}: {rec}")
