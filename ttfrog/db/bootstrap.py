import logging

from ttfrog.db.manager import db
from ttfrog.db import schema

from sqlalchemy.exc import IntegrityError

# move this to json or whatever
data = {
    'CharacterClass': [
        {
            'name': 'fighter',
            'hit_dice': '1d10',
            'hit_dice_stat': 'CON',
            'proficiencies': 'all armor, all shields, simple weapons, martial weapons',
            'saving_throws': ['STR, CON'],
            'skills': ['Acrobatics', 'Animal Handling', 'Athletics', 'History', 'Insight', 'Intimidation', 'Perception', 'Survival'],
        },
        {
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
        {'name': 'human', 'creature_type': 'humanoid'},
        {'name': 'dragonborn', 'creature_type': 'humanoid'},
        {'name': 'tiefling', 'creature_type': 'humanoid'},
    ],
    'Character': [
        {
            'id': 1,
            'name': 'Sabetha',
            'ancestry': 'tiefling',
            'character_class': ['fighter', 'rogue'],
            'level': 1,
            'armor_class': 10,
            'max_hit_points': 14,
            'hit_points': 14,
            'temp_hit_points': 0,
            'passive_perception': 10,
            'passive_insight': 10,
            'passive_investigation': 10,
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
