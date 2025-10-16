from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .entity import Entity
    from .entity_effect import EntityEffect
    from .feature import Feature


DamageHealSource: TypeAlias = "Entity | EntityEffect | Feature | None"


def damage_heal_source_to_string(damage_heal_source: DamageHealSource) -> str:
    if isinstance(damage_heal_source, Entity):
        return f"{damage_heal_source.name} at {damage_heal_source.pos}"
    elif isinstance(damage_heal_source, EntityEffect):
        return f"{damage_heal_source.name} effect"
    elif isinstance(damage_heal_source, Feature):
        return f"Feature {damage_heal_source.__class__.__name__} around {damage_heal_source.shape[0]}"
    elif damage_heal_source is None:
        return "unknown source"
