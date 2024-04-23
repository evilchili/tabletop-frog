from ttfrog.db import schema
from ttfrog.db.manager import db


def bootstrap():
    db.metadata.drop_all(bind=db.engine)
    db.init()
    with db.transaction():
        # ancestries
        human = schema.Ancestry(name="human")
        tiefling = schema.Ancestry(name="tiefling")
        tiefling.add_modifier(schema.Modifier(name="Ability Score Increase", target="intelligence", relative_value=1))
        tiefling.add_modifier(schema.Modifier(name="Ability Score Increase", target="charisma", relative_value=2))
        darkvision = schema.AncestryTrait(
            name="Darkvision",
            description=(
                "You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it "
                "were dim light. You can’t discern color in darkness, only shades of gray."
            ),
        )
        darkvision.add_modifier(schema.Modifier(name="Darkvision", target="vision_in_darkness", absolute_value=120))
        tiefling.add_trait(darkvision)

        # classes
        fighter = schema.CharacterClass(name="fighter", hit_dice="1d10", hit_dice_stat="CON")
        rogue = schema.CharacterClass(name="rogue", hit_dice="1d8", hit_dice_stat="DEX")

        # characters
        sabetha = schema.Character(name="Sabetha", ancestry=tiefling)
        sabetha.add_class(fighter, level=2)
        sabetha.add_class(rogue, level=3)

        bob = schema.Character(name="Bob", ancestry=human)

        # persist all the records we've created
        db.add_or_update([sabetha, bob])
