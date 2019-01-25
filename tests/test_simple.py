import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

import clavis
from tests.base import ClavisTestBase

Base = declarative_base()


class TestTable(Base):
    __tablename__ = "test_table"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text)


class SimpleTest(ClavisTestBase):
    def test_commit(self):
        with self.dbf.transaction() as txn:
            query = sa.insert(TestTable).values({TestTable.value: "x"})
            txn.session.execute(query)

        r = self.execute(
            "test", "select id from test_table where value = :v limit 1", v="x"
        )
        oid = r[0][0]

        r = self.execute("test", "select value from test_table where id = :id", id=oid)
        value = r[0][0]

        self.assertEqual(value, "x", "commit of insert failed")

    def test_rollback(self):
        with self.dbf.transaction() as txn:
            query = sa.insert(TestTable).values({TestTable.value: "x"})
            txn.session.execute(query)
            txn.session.rollback()

        r = self.execute(
            "test", "select id from test_table where value = :v limit 1", v="x"
        )
        self.assertFalse(r, "rollback failed")

    def setUp(self):
        db = self.setup_db("test", Base.metadata)
        self.dbf = clavis.TransactionFactory(database_url=db.url)

    def tearDown(self):
        self.cleanup()
