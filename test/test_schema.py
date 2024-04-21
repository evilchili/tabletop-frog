import json

from ttfrog.db import schema


def test_manage_character(db, classes_factory, ancestries_factory):
    with db.transaction():
        # load the fixtures so they are bound to the current session
        classes = classes_factory()
        ancestries = ancestries_factory()
        darkvision = db.session.query(schema.AncestryTrait).filter_by(name="Darkvision")[0]

        # create a human character (the default)
        char = schema.Character(name="Test Character")
        db.add_or_update(char)
        assert char.id == 1
        assert char.armor_class == 10
        assert char.name == "Test Character"
        assert char.ancestry.name == "human"
        assert darkvision not in char.traits

        # switch ancestry to tiefling
        char.ancestry = ancestries["tiefling"]
        db.add_or_update(char)
        char = db.session.get(schema.Character, 1)
        assert char.ancestry.name == "tiefling"
        assert darkvision in char.traits

        # assign a class and level
        char.add_class(classes["fighter"], level=1)
        db.add_or_update(char)
        assert char.levels == {"fighter": 1}
        assert char.level == 1
        assert char.class_attributes == {}

        # 'fighting style' is available, but not at this level
        fighting_style = char.classes["fighter"].attributes_by_level[2]["Fighting Style"]
        assert char.add_class_attribute(fighting_style, fighting_style.options[0]) is False
        db.add_or_update(char)
        assert char.class_attributes == {}

        # level up
        char.add_class(classes["fighter"], level=2)
        db.add_or_update(char)
        assert char.levels == {"fighter": 2}
        assert char.level == 2

        # Assert the fighting style is added automatically and idempotent...ly?
        assert char.class_attributes[fighting_style.name] == fighting_style.options[0]
        assert char.add_class_attribute(fighting_style, fighting_style.options[0]) is True
        db.add_or_update(char)

        # classes
        char.add_class(classes["rogue"], level=1)
        db.add_or_update(char)
        assert char.level == 3
        assert char.levels == {"fighter": 2, "rogue": 1}

        # remove a class
        char.remove_class(classes["rogue"])
        db.add_or_update(char)
        assert char.levels == {"fighter": 2}
        assert char.level == 2

        # remove remaining class by setting level to zero
        char.add_class(classes["fighter"], level=0)
        db.add_or_update(char)
        assert char.levels == {}

        # ensure we're not persisting any orphan records in the map tables
        dump = json.loads(db.dump())
        assert dump["class_map"] == []
        assert dump["character_class_attribute_map"] == []
