import json
import logging

from ttfrog.db.manager import db
from ttfrog.db.schema import TransactionLog


def record(previous, new):
    logging.debug(f"{previous = }, {new = }")
    diff = list((set(previous.items()) ^ set(dict(new).items())))
    if not diff:
        return

    rec = TransactionLog(
        source_table_name=new.__tablename__,
        primary_key=new.id,
        diff=json.dumps(diff),
    )
    with db.transaction():
        db.add(rec)
        logging.debug(f"Saved restore point: {dict(rec)}")
        return rec


def restore(rec, log_id=None):
    if log_id:
        log = db.query(TransactionLog).filter_by(id=log_id).one()
    else:
        log = db.query(TransactionLog).filter_by(source_table_name=rec.__tablename__, primary_key=rec.id).one()
    logging.debug(f"Located restore point {log = }")
    diff = json.loads(log.diff)
    updates = dict(diff[::2])
    if not updates:
        return
    logging.debug(f"{updates = }")
    with db.transaction():
        db.query(db.tables[log.source_table_name]).update(updates)
