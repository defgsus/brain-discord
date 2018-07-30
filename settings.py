
INFINITE_BOT_RUN = True

# can be a year, list of years, or "all"
FEFE_INDEX = "all"


try:
    from settings_local import *
except ImportError:
    pass