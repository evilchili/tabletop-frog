import logging

from ttfrog.db.manager import db
from ttfrog.db import schema

from sqlalchemy.exc import IntegrityError

# move this to json or whatever
data = {
    'CharacterClass': [
        {
            'id': 1,
            'name': 'fighter',
            'hit_dice': '1d10',
            'hit_dice_stat': 'CON',
            'proficiencies': 'all armor, all shields, simple weapons, martial weapons',
            'saving_throws': ['STR, CON'],
            'skills': ['Acrobatics', 'Animal Handling', 'Athletics', 'History', 'Insight', 'Intimidation', 'Perception', 'Survival'],
        },
        {
            'id': 2,
            'name': 'rogue',
            'hit_dice': '1d8',
            'hit_dice_stat': 'DEX',
            'proficiencies': 'simple weapons, hand crossbows, longswords, rapiers, shortswords',
            'saving_throws': ['DEX', 'INT'],
            'skills': ['Acrobatics', 'Athletics', 'Deception', 'Insight', 'Intimidation', 'Investigation', 'Perception', 'Performance', 'Persuasion', 'Sleight of Hand', 'Stealth'],
        },
    ],

    'Skill': [
        {'name': 'Acrobatics'},
        {'name': 'Animal Handling'},
        {'name': 'Athletics'},
        {'name': 'Deception'},
        {'name': 'History'},
        {'name': 'Insight'},
        {'name': 'Intimidation'},
        {'name': 'Investigation'},
        {'name': 'Perception'},
        {'name': 'Performance'},
        {'name': 'Persuasion'},
        {'name': 'Sleight of Hand'},
        {'name': 'Stealth'},
        {'name': 'Survival'},
    ],

    'Ancestry':  [
        {'id': 1, 'name': 'human', 'creature_type': 'humanoid'},
        {'id': 2, 'name': 'dragonborn', 'creature_type': 'humanoid'},
        {'id': 3, 'name': 'tiefling', 'creature_type': 'humanoid'},
    ],

    'Character': [
        {
            'id': 1,
            'name': 'Sabetha',
            'ancestry': 'human',
            'character_class': ['fighter', 'rogue'],
            'level': 1,
            'armor_class': 10,
            'max_hit_points': 14,
            'hit_points': 14,
            'temp_hit_points': 0,
            'speed': '30 ft.',
            'str': 16,
            'dex': 12,
            'con': 18,
            'int': 11,
            'wis': 12,
            'cha': 8,
            'proficiencies': 'all armor, all shields, simple weapons, martial weapons',
            'saving_throws': ['STR', 'CON'],
            'skills': ['Acrobatics', 'Animal Handling'],
        },
    ],

    'ClassAttribute': [
        {
            'character_class_id': 1,
            'name': 'Fighting Style',
            'value': 'Archery',
            'level': 1,
        },
    ],

    'AncestryTrait': [
        {
            'id': 1,
            'ancestry_id': 1,
            'description': '+1 to All Ability Scores',
            'level': 1,
        },
    ],

    'Modifier': [
        {'source_table_name': 'ancestry_trait', 'source_table_id': 1, 'value': '+1', 'type': 'stat', 'target': 'str'},
        {'source_table_name': 'ancestry_trait', 'source_table_id': 1, 'value': '+1', 'type': 'stat', 'target': 'dex'},
        {'source_table_name': 'ancestry_trait', 'source_table_id': 1, 'value': '+1', 'type': 'stat', 'target': 'con'},
        {'source_table_name': 'ancestry_trait', 'source_table_id': 1, 'value': '+1', 'type': 'stat', 'target': 'int'},
        {'source_table_name': 'ancestry_trait', 'source_table_id': 1, 'value': '+1', 'type': 'stat', 'target': 'wis'},
        {'source_table_name': 'ancestry_trait', 'source_table_id': 1, 'value': '+1', 'type': 'stat', 'target': 'cha'},
        {'source_table_name': 'class_attribute', 'source_table_id': 1, 'value': '+2', 'type': 'weapon ', 'target': 'ranged'},
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
                if 'UNIQUE constraint failed' in str(e):
                    logging.info(f"Skipping existing {table} {obj}")
                    continue
                raise
