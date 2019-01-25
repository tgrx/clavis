from contextlib import closing

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

import clavis
from tests.base import ClavisTestBase

Base = declarative_base()


class TestTable(Base):
    __tablename__ = "test_table"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text)


class PostponedQueriesTest(ClavisTestBase):
    def test_execute_postponed_on_context_exit(self):
        with self.dbf.transaction() as t:
            t.session.execute(sa.insert(TestTable).values({TestTable.value: "one"}))

            i_one = t.session.execute(
                sa.select([TestTable.id]).where(TestTable.value == "one").limit(1)
            ).scalar()

            t.postpone(
                sa.update(TestTable)
                .where(TestTable.id == i_one)
                .values({TestTable.value: "two"})
            )

        i_two = self.get_id("two")
        self.assertTrue(
            i_two, "failed execute of postponed update query on context exit"
        )

        self.assertEqual(
            i_one, i_two, "failed update of previous value with same id: id mismatch"
        )

        i_null = self.get_id("one")
        self.assertFalse(
            i_null, "failed execute of postponed update query on context exit"
        )

    def test_execute_postponed_on_explicit_txn_commit(self):
        with self.dbf.transaction() as t:
            t.session.execute(sa.insert(TestTable).values({TestTable.value: "one"}))
            t.postpone(sa.insert(TestTable).values({TestTable.value: "two"}))

            t.commit()

        i_one = self.get_id("one")
        self.assertTrue(i_one, "failed execute of insert query on explicit txn commit")

        i_two = self.get_id("two")
        self.assertTrue(
            i_two, "failed execute of postponed insert query on explicit txn commit"
        )

    def test_execute_postponed_on_explicit_txn_rollback(self):
        with self.dbf.transaction() as t:
            t.session.execute(sa.insert(TestTable).values({TestTable.value: "one"}))
            t.postpone(sa.insert(TestTable).values({TestTable.value: "two"}))

            t.rollback()

        i_one = self.get_id("one")
        self.assertFalse(
            i_one, "failed rollback of insert query on explicit txn rollback"
        )

        i_two = self.get_id("two")
        self.assertTrue(
            i_two, "failed execute of postponed insert query on explicit txn rollback"
        )

    def test_execute_postponed_on_explicit_session_commit(self):
        with self.dbf.transaction() as t:
            t.session.execute(sa.insert(TestTable).values({TestTable.value: "one"}))
            t.postpone(sa.insert(TestTable).values({TestTable.value: "two"}))

            t.session.commit()

        i_one = self.get_id("one")
        self.assertTrue(
            i_one, "failed execute of insert query on explicit session commit"
        )

        i_two = self.get_id("two")
        self.assertTrue(
            i_two, "failed execute of postponed insert query on explicit session commit"
        )

    def test_execute_postponed_on_explicit_session_rollback(self):
        with self.dbf.transaction() as t:
            t.session.execute(sa.insert(TestTable).values({TestTable.value: "one"}))
            t.postpone(sa.insert(TestTable).values({TestTable.value: "two"}))

            t.session.rollback()

        i_one = self.get_id("one")
        self.assertFalse(
            i_one, "failed rollback of insert query on explicit session rollback"
        )

        i_two = self.get_id("two")
        self.assertTrue(
            i_two,
            "failed execute of postponed insert query on explicit session rollback",
        )

    def test_execute_postponed_on_exception(self):
        with self.assertRaises(ZeroDivisionError):
            with self.dbf.transaction() as t:
                t.session.execute(sa.insert(TestTable).values({TestTable.value: "one"}))
                t.postpone(sa.insert(TestTable).values({TestTable.value: "two"}))

                raise ZeroDivisionError

        i_one = self.get_id("one")
        self.assertFalse(i_one, "failed rollback of insert query on exception")

        i_two = self.get_id("two")
        self.assertTrue(i_two, "failed execute of postponed insert query on exception")

    def setUp(self):
        super().setUp()
        db = self.setup_db("test", Base.metadata)
        self.engine = db.engine
        self.dbf = clavis.TransactionFactory(database_url=db.url)

    def tearDown(self):
        self.cleanup()
        super().tearDown()

    def get_value(self, object_id):
        query = sa.text("select value from test_table where id = :arg")
        with closing(self.engine.connect()) as conn:
            value = conn.execute(query, arg=object_id).scalar()
        return value

    def get_id(self, object_value):
        query = sa.text("select id from test_table where value = :arg limit 1")
        with closing(self.engine.connect()) as conn:
            value = conn.execute(query, arg=object_value).scalar()
        return value
