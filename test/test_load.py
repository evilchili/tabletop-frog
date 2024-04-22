import pytest

from ttfrog.db import schema


@pytest.mark.skip
def test_many_records(db):
    with db.transaction():
        for i in range(1, 1000):
            obj = schema.Ancestry(name=f"{i}-ancestry")
            db.add_or_update(obj)
            assert obj.id == i

        for i in range(1, 1000):
            obj = schema.Character(name=f"{i}-char")
            db.add_or_update(obj)
