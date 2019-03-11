from sqlalchemy.orm import Session as _SqlAlchemySession

from . import states


class Session(_SqlAlchemySession):
    def __init__(self, *args, **kwargs):
        self.__origin = kwargs.pop("origin", None)

        super().__init__(*args, **kwargs)

    def flush(self, *args, **kwargs):
        super().flush(*args, **kwargs)
        self.expire_all()

    def commit(self):
        self.flush()

        raise states.Committed(self.__origin)

    def rollback(self, internal: bool = False):
        rollback_result = super().rollback()

        if internal:
            return rollback_result
        else:
            raise states.RolledBack(self.__origin)

    def begin_nested(self):
        raise NotImplementedError()

    @property
    def txn(self):
        return self.__origin
