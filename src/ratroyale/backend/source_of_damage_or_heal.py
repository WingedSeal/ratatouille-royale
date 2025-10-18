from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .entity import Entity
    from .entity_effect import EntityEffect
    from .feature import Feature


SourceOfDamageOrHeal: TypeAlias = "Entity | EntityEffect | Feature | None"
