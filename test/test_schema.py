from ttfrog.db import schema


def test_create_character(db, classes, ancestries):
    with db.transaction():
        darkvision = db.session.query(schema.AncestryTrait).filter_by(name="Darkvision")[0]

        # create a human character (the default)
        char = schema.Character(name="Test Character")
        db.add(char)
        assert char.id == 1
        assert char.armor_class == 10
        assert char.name == "Test Character"
        assert char.ancestry.name == "human"
        assert darkvision not in char.traits

        # switch ancestry to tiefling
        char.ancestry = ancestries["tiefling"]
        db.add(char)
        char = db.session.get(schema.Character, 1)
        assert char.ancestry.name == "tiefling"
        assert darkvision in char.traits

        # assign a class and level
        char.add_class(classes["fighter"], level=1)
        db.add(char)
        assert char.levels == {"fighter": 1}
        assert char.level == 1
        assert char.class_attributes == []

        # level up
        char.add_class(classes["fighter"], level=2)
        db.add(char)
        assert char.levels == {"fighter": 2}
        assert char.level == 2
        assert char.class_attributes == []

        # multiclass
        char.add_class(classes["rogue"], level=1)
        db.add(char)
        assert char.level == 3
        assert char.levels == {"fighter": 2, "rogue": 1}

        # remove a class
        char.remove_class(classes["rogue"])
        db.add(char)
        assert char.levels == {"fighter": 2}
        assert char.level == 2

        # remove all remaining classes
        char.remove_class(classes["fighter"])
        db.add(char)

        # ensure we're not persisting any orphan records in the map table
        dump = db.dump()
        assert dump["class_map"] == []
