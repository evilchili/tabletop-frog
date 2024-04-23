import json

from ttfrog.db import schema


def test_manage_character(db, classes_factory, ancestries_factory):
    with db.transaction():
        # load the fixtures so they are bound to the current session
        classes = classes_factory()
        ancestries = ancestries_factory()
        darkvision = db.AncestryTrait.filter_by(name="Darkvision")[0]

        # create a human character (the default)
        char = schema.Character(name="Test Character")
        db.add_or_update(char)
        assert char.id == 1
        assert char.name == "Test Character"
        assert char.ancestry.name == "human"
        assert char.AC == 10
        assert char.HP == 10
        assert char.STR == 10
        assert char.DEX == 10
        assert char.CON == 10
        assert char.INT == 10
        assert char.WIS == 10
        assert char.CHA == 10
        assert darkvision not in char.traits

        # switch ancestry to tiefling
        char.ancestry = ancestries["tiefling"]
        db.add_or_update(char)
        char = db.session.get(schema.Character, 1)
        assert char.ancestry.name == "tiefling"
        assert darkvision in char.traits

        # switch ancestry to dragonborn and assert darkvision persists
        char.ancestry = ancestries["dragonborn"]
        db.add_or_update(char)
        assert darkvision in char.traits

        # switch ancestry to human and assert darkvision is removed
        char.ancestry = ancestries["human"]
        db.add_or_update(char)
        assert darkvision not in char.traits

        # assign a class and level
        char.add_class(classes["fighter"], level=1)
        db.add_or_update(char)
        assert char.levels == {"fighter": 1}
        assert char.level == 1
        assert char.class_attributes == {}

        # 'fighting style' is available, but not at this level
        fighter = classes["fighter"]
        fighting_style = fighter.attributes_by_level[2]["Fighting Style"]
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


def test_ancestries(db):
    with db.transaction():
        # create the Pygmy Orc ancestry
        porc = schema.Ancestry(
            name="Pygmy Orc",
            size="Small",
            walk_speed=25,
        )
        db.add_or_update(porc)
        assert porc.name == "Pygmy Orc"
        assert porc.creature_type == "humanoid"
        assert porc.size == "Small"
        assert porc.speed == 25

        # create the Relentless Endurance trait and add it to the Orc
        endurance = schema.AncestryTrait(name="Relentless Endurance")
        db.add_or_update(endurance)
        porc.add_trait(endurance, level=1)
        db.add_or_update(porc)
        assert endurance in porc.traits

        # add a +1 STR modifier
        str_plus_one = schema.Modifier(
            name="STR+1 (Pygmy Orc)",
            target="strength",
            relative_value=1,
            description="Your Strength score is increased by 1.",
        )
        assert porc.add_modifier(str_plus_one) is True
        assert porc.add_modifier(str_plus_one) is False  # test idempotency
        assert str_plus_one in porc.modifiers["strength"]

        # now create an orc character and assert it gets traits and modifiers
        grognak = schema.Character(name="Grognak the Mighty", ancestry=porc)
        db.add_or_update(grognak)
        assert endurance in grognak.traits

        # verify the strength bonus is applied
        assert grognak.strength == 10
        assert str_plus_one in grognak.modifiers["strength"]
        assert grognak.STR == 11


def test_modifiers(db, classes_factory, ancestries_factory):
    with db.transaction():
        classes_factory()
        ancestries = ancestries_factory()

        # no modifiers; speed is ancestry speed
        carl = schema.Character(name="Carl", ancestry=ancestries["elf"])
        marx = schema.Character(name="Marx", ancestry=ancestries["human"])
        db.add_or_update([carl, marx])
        assert carl.speed == carl.ancestry.speed == 30

        cold = schema.Modifier(target="speed", relative_value=-10, name="Cold")
        hasted = schema.Modifier(target="speed", multiply_value=2.0, name="Hasted")
        slowed = schema.Modifier(target="speed", multiply_value=0.5, name="Slowed")
        restrained = schema.Modifier(target="speed", absolute_value=0, name="Restrained")
        reduced = schema.Modifier(target="size", new_value="Tiny", name="Reduced")

        # reduce speed by 10
        assert carl.add_modifier(cold)
        assert carl.speed == 20

        # make sure modifiers only apply to carl. Carl is having a bad day.
        assert marx.speed == 30

        # speed is doubled
        assert carl.remove_modifier(cold)
        assert carl.add_modifier(hasted)
        assert carl.speed == 60

        # speed is halved
        assert carl.remove_modifier(hasted)
        assert carl.add_modifier(slowed)
        assert carl.speed == 15

        # speed is 0
        assert carl.add_modifier(restrained)
        assert carl.speed == 0

        # no longer restrained, but still slowed
        assert carl.remove_modifier(restrained)
        assert carl.speed == 15

        # back to normal
        assert carl.remove_modifier(slowed)
        assert carl.speed == carl.ancestry.speed

        # modifiers can modify string values too
        assert carl.add_modifier(reduced)
        assert carl.size == "Tiny"
