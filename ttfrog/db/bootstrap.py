import logging

from ttfrog.db import db, session


# move this to json or whatever
data = {
    'ancestry':  [
        {'name': 'human'},
        {'name': 'dragonborn'},
        {'name': 'tiefling'},
    ],
    'character': [
        {'name': 'Sabetha', 'ancestry_name': 'tiefling', 'level': 10, 'str': 10, 'dex': 10, 'con': 10, 'int': 10, 'wis': 10, 'cha': 10},
    ]
}


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
            stmt = table.insert().values(**rec).prefix_with("OR IGNORE")
            result, error = db.execute(stmt)
            if error:
                raise RuntimeError(error)

            rec['id'] = result.inserted_primary_key[0]
            if rec['id'] == 0:
                logging.info(f"Skipped existing {table_name} {rec}")
                continue

            if 'slug' in table.columns:
                rec['slug'] = db.slugify(rec)
                db.update(table, **rec)
            logging.info(f"Created {table_name} {rec}")
