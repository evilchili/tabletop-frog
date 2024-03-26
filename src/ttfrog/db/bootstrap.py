import logging

from sqlalchemy.exc import IntegrityError

from ttfrog.db import schema
from ttfrog.db.manager import db

# move this to json or whatever
data = {
    "CharacterClass": [
        {
            "id": 1,
            "name": "fighter",
            "hit_dice": "1d10",
            "hit_dice_stat": "CON",
            "proficiencies": "all armor, all shields, simple weapons, martial weapons",
            "saving_throws": ["STR, CON"],
            "skills": [
                "Acrobatics",
                "Animal Handling",
                "Athletics",
                "History",
                "Insight",
                "Intimidation",
                "Perception",
                "Survival",
            ],
        },
        {
            "id": 2,
            "name": "rogue",
            "hit_dice": "1d8",
            "hit_dice_stat": "DEX",
            "proficiencies": "simple weapons, hand crossbows, longswords, rapiers, shortswords",
            "saving_throws": ["DEX", "INT"],
            "skills": [
                "Acrobatics",
                "Athletics",
                "Deception",
                "Insight",
                "Intimidation",
                "Investigation",
                "Perception",
                "Performance",
                "Persuasion",
                "Sleight of Hand",
                "Stealth",
            ],
        },
    ],
    "Skill": [
        {"name": "Acrobatics"},
        {"name": "Animal Handling"},
        {"name": "Athletics"},
        {"name": "Deception"},
        {"name": "History"},
        {"name": "Insight"},
        {"name": "Intimidation"},
        {"name": "Investigation"},
        {"name": "Perception"},
        {"name": "Performance"},
        {"name": "Persuasion"},
        {"name": "Sleight of Hand"},
        {"name": "Stealth"},
        {"name": "Survival"},
    ],
    "Ancestry": [
        {"id": 1, "name": "human", "creature_type": "humanoid"},
        {"id": 2, "name": "dragonborn", "creature_type": "humanoid"},
        {"id": 3, "name": "tiefling", "creature_type": "humanoid"},
        {"id": 4, "name": "elf", "creature_type": "humanoid"},
    ],
    "AncestryTrait": [
        {
            "id": 1,
            "name": "+1 to All Ability Scores",
        },
        {
            "id": 2,
            "name": "Breath Weapon",
        },
        {
            "id": 3,
            "name": "Darkvision",
        },
    ],
    "AncestryTraitMap": [
        {"ancestry_id": 1, "ancestry_trait_id": 1, "level": 1},  # human +1 to scores
        {"ancestry_id": 2, "ancestry_trait_id": 2, "level": 1},  # dragonborn breath weapon
        {"ancestry_id": 3, "ancestry_trait_id": 3, "level": 1},  # tiefling darkvision
        {"ancestry_id": 2, "ancestry_trait_id": 2, "level": 1},  # elf darkvision
    ],
    "CharacterClassMap": [
        {
            "character_id": 1,
            "character_class_id": 1,
            "level": 2,
        },
        {
            "character_id": 1,
            "character_class_id": 2,
            "level": 3,
        },
    ],
    "Character": [
        {
            "id": 1,
            "name": "Sabetha",
            "ancestry_id": 1,
            "armor_class": 10,
            "max_hit_points": 14,
            "hit_points": 14,
            "temp_hit_points": 0,
            "speed": 30,
            "str": 16,
            "dex": 12,
            "con": 18,
            "int": 11,
            "wis": 12,
            "cha": 8,
            "proficiencies": "all armor, all shields, simple weapons, martial weapons",
            "saving_throws": ["STR", "CON"],
            "skills": ["Acrobatics", "Animal Handling"],
        },
    ],
    "ClassAttribute": [
        {"id": 1, "name": "Fighting Style"},
        {"id": 2, "name": "Another Attribute"},
    ],
    "ClassAttributeOption": [
        {"id": 1, "attribute_id": 1, "name": "Archery"},
        {"id": 2, "attribute_id": 1, "name": "Battlemaster"},
        {"id": 3, "attribute_id": 2, "name": "Another Option 1"},
        {"id": 4, "attribute_id": 2, "name": "Another Option 2"},
    ],
    "ClassAttributeMap": [
        {"class_attribute_id": 1, "character_class_id": 1, "level": 2},  # Fighter: Fighting Style
        {"class_attribute_id": 2, "character_class_id": 1, "level": 1},  # Fighter: Another Attr
    ],
    "CharacterClassAttributeMap": [
        {"character_id": 1, "class_attribute_id": 2, "option_id": 4},  # Sabetha, another option, option 2
        {"character_id": 1, "class_attribute_id": 1, "option_id": 1},  # Sabetha, fighting style, archery
    ],
    "Modifier": [
        # Humans
        {"source_table_name": "ancestry_trait", "source_table_id": 1, "value": "+1", "type": "stat", "target": "str"},
        {"source_table_name": "ancestry_trait", "source_table_id": 1, "value": "+1", "type": "stat", "target": "dex"},
        {"source_table_name": "ancestry_trait", "source_table_id": 1, "value": "+1", "type": "stat", "target": "con"},
        {"source_table_name": "ancestry_trait", "source_table_id": 1, "value": "+1", "type": "stat", "target": "int"},
        {"source_table_name": "ancestry_trait", "source_table_id": 1, "value": "+1", "type": "stat", "target": "wis"},
        {"source_table_name": "ancestry_trait", "source_table_id": 1, "value": "+1", "type": "stat", "target": "cha"},
        # Dragonborn
        {
            "source_table_name": "ancestry_trait",
            "source_table_id": 2,
            "value": "60",
            "type": "attribute ",
            "target": "Darkvision",
        },
        {"source_table_name": "ancestry_trait", "source_table_id": 2, "value": "+1", "type": "stat", "target": ""},
        {"source_table_name": "ancestry_trait", "source_table_id": 2, "value": "+1", "type": "stat", "target": ""},
        # Fighting Style: Archery
        {
            "source_table_name": "class_attribute",
            "source_table_id": 1,
            "value": "+2",
            "type": "weapon ",
            "target": "ranged",
        },
    ],
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
                if "UNIQUE constraint failed" in str(e):
                    logging.info(f"Skipping existing {table} {obj}")
                    continue
                raise
