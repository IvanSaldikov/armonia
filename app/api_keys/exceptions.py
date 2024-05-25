class APIKeyNotFound(Exception):
    ...


class APIKeyExceededTotalLimit(Exception):
    ...


class APIKeyExceededDailyLimit(Exception):
    ...


class APIKeyBlocked(Exception):
    ...


class APIKeyExceededAllowedNumberOfKeys(Exception):
    ...
