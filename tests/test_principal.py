import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

import clavis
from tests.base import ClavisTestBase

Base = declarative_base()


class TestTable(Base):
    __tablename__ = "test_table"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text)


class PrincipalTest(ClavisTestBase):
    def test_commit_on_context_exit(self):
        with self.dbf.transaction() as txn:
            query = sa.insert(TestTable).values({TestTable.value: "x"})
            txn.session.execute(query)

        r = self.execute(
            "test", "select id from test_table where value = :v limit 1", v="x"
        )
        self.assertTrue(r, "failed implicit commit on context exit")
        self.assertEqual(1, len(r), "failed implicit commit on context exit")
        self.assertTrue(r[0], "failed implicit commit on context exit")

        oid = r[0][0]
        self.assertTrue(oid, "failed implicit commit on context exit")

        r = self.execute("test", "select value from test_table where id = :id", id=oid)
        self.assertTrue(r, "failed implicit commit on context exit")
        self.assertEqual(1, len(r), "failed implicit commit on context exit")
        self.assertTrue(r[0], "failed implicit commit on context exit")

        value = r[0][0]
        self.assertEqual(value, "x", "failed implicit commit on context exit")

    def test_rollback_on_explicit_rollback(self):
        with self.dbf.transaction() as txn:
            query = sa.insert(TestTable).values({TestTable.value: "x"})
            txn.session.execute(query)
            txn.session.rollback()

        r = self.execute(
            "test", "select id from test_table where value = :v limit 1", v="x"
        )
        self.assertFalse(r, "failed rollback on explicit rollback")

    def setUp(self):
        super().setUp()
        db = self.setup_db("test", Base.metadata)
        self.dbf = clavis.TransactionFactory(database_url=db.url)

    def tearDown(self):
        self.cleanup()
        super().tearDown()
