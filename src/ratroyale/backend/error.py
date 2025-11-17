from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .entity import Entity
    from .feature import Feature


class RatRoyaleBackendError(Exception):
    pass


class EntityInvalidPosError(RatRoyaleBackendError):
    pass


class NotEnoughCrumbError(RatRoyaleBackendError):
    pass


class NotEnoughCheeseError(RatRoyaleBackendError):
    pass


class NotEnoughSkillStaminaError(RatRoyaleBackendError):
    pass


class NotEnoughMoveStaminaError(RatRoyaleBackendError):
    pass


class InvalidMoveTargetError(RatRoyaleBackendError):
    pass


class RodentEffectNotOnRodentError(RatRoyaleBackendError):
    pass


class ShortHandSkillCallbackError(RatRoyaleBackendError):
    """
    select_targetable() allows alternative method to pass callback.
    Instead of passing callback directly, a list of callback can be passed
    and the function will generate a new callback and chain on its own.
    However the limitation is that if one of the callback return fail,
    it doesn't know what to do. Hence this exception.
    """

    pass


class NotAITurnError(RatRoyaleBackendError):
    pass


class GameManagerActionPerformedInSelectingMode(RatRoyaleBackendError):
    pass


class GameManagerSkillCallBackInNonSelectingMode(RatRoyaleBackendError):
    pass


class AICantPathfind(RatRoyaleBackendError):
    pass


class InvalidDeckError(RatRoyaleBackendError):
    pass


class UpdatingTheDeadError(RatRoyaleBackendError):
    def __init__(self, the_dead: "Feature | Entity") -> None:
        assert the_dead.is_dead
        super().__init__(f"{the_dead} is already dead but it is getting updated")
