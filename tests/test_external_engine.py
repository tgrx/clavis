import os

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from tests.base import ClavisTestBase

Base = declarative_base()


class TestTable(Base):
    __tablename__ = "test_table"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text)


class ExternalEngineTest(ClavisTestBase):
    def test_engine(self):
        print(f"here: test")

        import clavis

        with clavis.Transaction(self.db_url) as txn:
            self.assertIsNot(self.engine, txn.engine)
            txn.session.execute(sa.insert(TestTable).values({TestTable.value: "1"}))

        with clavis.Transaction(self.db_url) as txn_2:
            self.assertIsNot(self.engine, txn_2.engine)
            txn_2.session.execute(sa.insert(TestTable).values({TestTable.value: "2"}))

        with clavis.Transaction(self.db_url, engine=self.engine) as txn:
            self.assertIs(self.engine, txn.engine)
            txn.session.execute(sa.insert(TestTable).values({TestTable.value: "3"}))

        with clavis.Transaction(self.db_url, engine=self.engine) as txn_2:
            self.assertIs(self.engine, txn_2.engine)
            txn_2.session.execute(sa.insert(TestTable).values({TestTable.value: "4"}))

        tf = clavis.TransactionFactory(self.db_url)
        with tf.transaction() as txn:
            self.assertIsNot(self.engine, txn.engine)
            txn.session.execute(sa.insert(TestTable).values({TestTable.value: "5"}))

        tf = clavis.TransactionFactory(self.db_url, engine=self.engine)
        with tf.transaction() as txn:
            self.assertIs(self.engine, txn.engine)
            txn.session.execute(sa.insert(TestTable).values({TestTable.value: "6"}))

            q = sa.select([TestTable.id, TestTable.value])
            rows = txn.session.execute(q).fetchall()
            self.assertEqual(6, len(rows))

    def setUp(self):
        super().setUp()
        db = self.setup_db("test", Base.metadata)
        self.engine = db.engine
        self.db_url = db.url

    def tearDown(self):
        self.cleanup()
