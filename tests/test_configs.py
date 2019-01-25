import os

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from tests.base import ClavisTestBase

Base = declarative_base()


class TestTable(Base):
    __tablename__ = "test_table"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text)


class ConfigTest(ClavisTestBase):
    def test_config_order(self):
        print(f"here: test")

        import clavis

        with clavis.Transaction() as txn:
            txn.session.execute(sa.insert(TestTable).values({TestTable.value: "env"}))

        clavis.configure(self.db_urls["conf"])
        with clavis.Transaction() as txn:
            txn.session.execute(sa.insert(TestTable).values({TestTable.value: "conf"}))

        tf = clavis.TransactionFactory(self.db_urls["tf"])
        with tf.transaction() as txn:
            txn.session.execute(sa.insert(TestTable).values({TestTable.value: "tf"}))

        with clavis.Transaction(self.db_urls["txn"]) as txn:
            txn.session.execute(sa.insert(TestTable).values({TestTable.value: "txn"}))

        for name, url in self.db_urls.items():
            q = sa.select([TestTable.id, TestTable.value])

            with clavis.Transaction(url) as txn:
                rows = txn.session.execute(q).fetchall()
                self.assertEqual(1, len(rows), f'config failed for "{name}"')
                item = rows[0]
                self.assertEqual(item.value, name, f'config failed for "{name}"')

    def setUp(self):
        super().setUp()

        self.db_urls = {
            name: self.setup_db("db_{}".format(name), Base.metadata).url
            for name in {"env", "conf", "tf", "txn"}
        }

        os.environ["DATABASE_URL"] = self.db_urls["env"]
        from clavis.conf import settings
        from clavis.conf.loader import load_from_global_envs

        load_from_global_envs(settings)

    def tearDown(self):
        self.cleanup()
