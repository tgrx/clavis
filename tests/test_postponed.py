import os
from contextlib import closing
from unittest import TestCase

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

import clavis

DATABASE_URL = "sqlite:///testdb.sqlite"

Base = declarative_base()


class TestTable(Base):
    __tablename__ = "test_table"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text)


engine = sa.create_engine(DATABASE_URL)


def get_value(object_id):
    query = sa.text("select value from test_table where id = :arg")
    with closing(engine.connect()) as conn:
        value = conn.execute(query, arg=object_id).scalar()
    return value


def get_id(object_value):
    query = sa.text("select id from test_table where value = :arg limit 1")
    with closing(engine.connect()) as conn:
        value = conn.execute(query, arg=object_value).scalar()
    return value


class PostponedQueriesTest(TestCase):
    def test_flow(self):
        with clavis.Transaction() as t:
            query = sa.insert(TestTable).values({TestTable.value: "x"})
            t.session.execute(query)

        x = get_id("x")
        value = get_value(x)
        self.assertEqual(value, "x", "commit of insert failed")

        with clavis.Transaction() as t:
            t.session.execute(sa.insert(TestTable).values({TestTable.value: "y"}))

            y = t.session.execute(
                sa.select([TestTable.id]).where(TestTable.value == "y").limit(1)
            ).scalar()

            t.postpone(
                sa.update(TestTable)
                .where(TestTable.id == y)
                .values({TestTable.value: "yyy"})
            )

        yyy = get_id("yyy")
        self.assertTrue(yyy, "postponed-after-commit update failed")
        self.assertEqual(y, yyy, "general data corruption")

        with clavis.Transaction() as t:
            t.session.execute(
                sa.update(TestTable)
                .values({TestTable.value: "yy"})
                .where(TestTable.id == yyy)
            )

            t.postpone(
                sa.update(TestTable)
                .where(TestTable.id == yyy)
                .values({TestTable.value: "yyy"})
            )

            t.session.rollback()

        yyy = get_id("yyy")
        self.assertTrue(yyy, "postponed-after-rollback update failed")

        yy = get_id("yy")
        self.assertIsNone(yy, "rollback failed")

        with self.assertRaises(ZeroDivisionError):
            with clavis.Transaction() as t:
                t.session.execute(sa.delete(TestTable).where(TestTable.id == yyy))

                t.postpone(
                    sa.update(TestTable)
                    .where(TestTable.id == yyy)
                    .values({TestTable.value: "yy"})
                )

                raise ZeroDivisionError()

        yyy = get_id("yyy")
        self.assertIsNone(yyy, "postponed-after-exception update failed")

        yy = get_id("yy")
        self.assertTrue(yy, "postponed-after-exception update failed")

    def setUp(self):
        with open("./testdb.sqlite", "w"):
            pass
        TestTable.metadata.create_all(engine)

        clavis.configure(DATABASE_URL)

    def tearDown(self):
        os.remove("./testdb.sqlite")
