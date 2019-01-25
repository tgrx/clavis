import os
from unittest import TestCase

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

import clavis

DATABASE_1_FILE = "testdb_1.sqlite"
DATABASE_1_URL = "sqlite:///{}".format(DATABASE_1_FILE)

DATABASE_2_FILE = "testdb_2.sqlite"
DATABASE_2_URL = "sqlite:///{}".format(DATABASE_2_FILE)

Base = declarative_base()


class TestTable(Base):
    __tablename__ = "test_table"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text)


class RuntimeDbSetupTest(TestCase):
    def test_multiple_db(self):
        with clavis.Transaction() as t:
            t.session.execute("insert into test_table(value) values ('1');")

        with clavis.Transaction(DATABASE_2_URL) as t:
            r = t.session.execute("select value from test_table;").fetchall()
            self.assertListEqual(r, [])

        with clavis.Transaction() as t:
            r = t.session.execute("select value from test_table;").fetchall()
            self.assertListEqual(r, [("1",)])

        with clavis.Transaction(DATABASE_1_URL) as t:
            r = t.session.execute("select value from test_table;").fetchall()
            self.assertListEqual(r, [("1",)])

    def setUp(self):
        for dbf in (DATABASE_1_FILE, DATABASE_2_FILE):
            with open("./{}".format(dbf), "w"):
                pass

        for url in (DATABASE_1_URL, DATABASE_2_URL):
            engine = sa.create_engine(url)
            TestTable.metadata.create_all(engine)

        clavis.configure(DATABASE_1_URL)

    def tearDown(self):
        pass
        for dbf in (DATABASE_1_FILE, DATABASE_2_FILE):
            os.remove("./{}".format(dbf))
