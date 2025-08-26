class RatRoyaleBackendError(Exception):
    pass


class EntityInvalidPosError(RatRoyaleBackendError):
    pass


class NotEnoughCrumbError(RatRoyaleBackendError):
    pass
