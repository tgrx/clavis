from dynaconf import LazySettings

from .loader import load_from_global_envs

settings = LazySettings()
load_from_global_envs(settings)
