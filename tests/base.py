import os
import typing as ty
from contextlib import closing
from pathlib import Path
from unittest import TestCase

import sqlalchemy as sa
from sqlalchemy.engine.base import Engine


class _Db(ty.NamedTuple):
    name: str
    path: str
    url: str
    engine: ty.Optional[Engine]


class ClavisTestBase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._databases = {}

    def setup_db(self, name, metadata) -> _Db:
        self.validate_name(name)
        db = self.create_db(name)
        metadata.create_all(db.engine)
        self._databases[name] = db
        return db

    def validate_name(self, name):
        if name in self._databases:
            raise ValueError(f"database {name} already exists")

    @staticmethod
    def create_db(name) -> _Db:
        """
        Creates a new DB, returning path to db file
        """
        path = f"./test_db_{name}.sqlite"
        with open(path, "w"):
            pass

        path = Path(path).resolve().as_posix()
        url = f"sqlite:///{path}"

        engine = sa.create_engine(url)

        return _Db(name=name, path=path, engine=engine, url=url)

    def drop_db(self, name):
        db: ty.Optional[_Db] = self._databases.get(name)
        if not db:
            return

        os.remove(db.path)

    def init(self):
        self._databases = {}

    def cleanup(self):
        for db in self._databases.values():
            os.remove(db.path)
        self.init()

    def execute(self, name, query, **params):
        db = self._databases[name]

        with closing(db.engine.connect()) as conn:
            result = conn.execute(query, **params).fetchall()
            return result
