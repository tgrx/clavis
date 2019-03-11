import typing as ty
from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import sql
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from . import conf
from . import errors
from . import session
from . import states


class Transaction(object):
    def __init__(
        self,
        database_url: ty.Optional[str] = None,
        echo: ty.Optional[bool] = None,
        engine: ty.Optional[Engine] = None,
    ):
        self._database_url = (
            database_url
            if database_url is not None
            else conf.settings.get("DATABASE_URL")
        )
        self._echo = echo if echo is not None else conf.settings.get("DATABASE_ECHO")

        self._engine = None
        self._external_engine = engine
        self._conn = None
        self._txn = None
        self._session = None
        self._postponed = OrderedDict()

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session(self) -> Session:
        return self._session

    def postpone(self, *queries) -> ty.Union[ty.Tuple[int], int]:
        if not queries:
            raise ValueError(
                f"{Transaction.__name__}.postpone() requires at least one query to postpone"
            )

        result = []

        for idx, query in enumerate(queries, 1):
            if not isinstance(query, (sql.Insert, sql.Update, sql.Delete)):
                raise ValueError(f"query {idx}: unsupported type {type(query)}")

            h = hash(query)
            self._postponed[h] = query

            result.append(h)

        return tuple(result) if len(result) > 1 else result[0]

    def remove_postponed(self, query_id: int) -> ty.NoReturn:
        if query_id in self._postponed:
            del self._postponed[query_id]

    def commit(self) -> ty.NoReturn:
        if not self._session:
            raise states.Committed()

        self.session.commit()

    def rollback(self) -> ty.NoReturn:
        if not self._session:
            raise states.RolledBack()

        self.session.rollback()

    def __enter__(self):
        self.__verify_reentrance()
        self.__connect_and_begin()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.__commit()
            finalized = None

        elif exc_type is states.Committed:
            self.__commit()
            finalized = True

        elif exc_type is states.RolledBack:
            self.__rollback()
            finalized = True

        else:
            self.__rollback()
            finalized = False

        self.__cleanup()

        self.__execute_postponed()

        return finalized

    def __verify_reentrance(self):
        if any((self._engine, self._conn, self._txn, self._session)):
            raise errors.AlreadyEnteredError()

    def __connect_and_begin(self):
        self.__init_engine()

        self._conn = self._engine.connect()
        self._txn = self._conn.begin()
        self._session = session.Session(bind=self._conn, origin=self)

    def __init_engine(self):
        if self._external_engine:
            self._engine = self._external_engine
        else:
            self.__verify_db()

            url = self._database_url

            self._engine = sa.create_engine(
                url, encoding="utf-8", poolclass=NullPool, echo=self._echo
            )

    def __verify_db(self):
        if not self._database_url:
            raise errors.BadDatabaseError("database is not configured")

    def __commit(self):
        self._session.flush()
        self._txn.commit()

    def __rollback(self):
        self._session.rollback(internal=True)
        self._txn.rollback()

    def __cleanup(self):
        self._conn.close()

        self._conn = None
        self._txn = None
        self._session = None

    def __execute_postponed(self):
        if not self._postponed:
            return

        with Transaction(self._database_url, self._echo) as txn:
            for q in self._postponed.values():
                txn.session.execute(q)
