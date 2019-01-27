import os

from . import global_vars as _v


def load_from_global_envs(settings):
    global_vars = {
        _var: os.getenv(_var)
        for _var in (_v.VAR_DATABASE_URL, _v.VAR_DATABASE_ECHO)
        if os.getenv(_var) is not None
    }
    settings.update(global_vars)
