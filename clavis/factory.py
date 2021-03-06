import typing as ty

from sqlalchemy.engine.base import Engine

from .conf import settings
from .transaction import Transaction


class TransactionFactory:
    def __init__(
        self,
        database_url: ty.Optional[str] = None,
        echo: ty.Optional[bool] = None,
        engine: ty.Optional[Engine] = None,
    ):
        self.database_url = (
            database_url if database_url is not None else settings.get("DATABASE_URL")
        )
        self.echo = echo if echo is not None else settings.get("DATABASE_ECHO")
        self.engine = engine

    def transaction(self):
        return Transaction(
            database_url=self.database_url, echo=self.echo, engine=self.engine
        )
