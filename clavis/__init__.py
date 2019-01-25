import typing as ty

from .factory import TransactionFactory
from .transaction import Transaction

name = "clavis"


def configure(database_url: str, echo: ty.Optional[bool] = None):
    if not database_url:
        from clavis.errors import BadDatabaseError

        raise BadDatabaseError("bad database url: cannot be empty")

    from .conf import settings
    from .conf import global_vars as gv

    settings.set(gv.VAR_DATABASE_URL, database_url)

    if echo is not None:
        settings.set(gv.VAR_DATABASE_ECHO, bool(echo))


__all__ = ("Transaction", "TransactionFactory")
