class RatRoyaleBackendError(Exception):
    pass


class EntityInvalidPosError(RatRoyaleBackendError):
    pass


class NotEnoughCrumbError(RatRoyaleBackendError):
    pass


class InvalidMoveTargetError(RatRoyaleBackendError):
    pass


class RodentEffectNotOnRodentError(RatRoyaleBackendError):
    pass
