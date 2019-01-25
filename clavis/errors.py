class ClavisError(Exception):
    pass


class BadDatabaseError(ClavisError):
    pass


class AlreadyEnteredError(ClavisError):
    pass
