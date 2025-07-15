import os
from .db_config import get_env_obj

env = os.environ.get("env", default="DEV")
configuration_obj = get_env_obj(env)
access = configuration_obj.get("env", {})
