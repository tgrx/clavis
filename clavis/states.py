import typing as ty
import weakref


class StepState(Exception):
    def __init__(self, origin: ty.Optional[object] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__origin = None
        if origin:
            self.__origin = weakref.ref(origin)

    @property
    def origin(self):
        return self.__origin() if self.__origin else None


class RolledBack(StepState):
    pass


class Committed(StepState):
    pass
