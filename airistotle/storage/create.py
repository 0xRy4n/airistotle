from tinydb import TinyDB
from ..settings import DB_LOCATION

if DB_LOCATION.exists():
    raise RuntimeError(
        "Database already exists. Remove it if you'd like to re-create it."
    )

db = TinyDB(DB_LOCATION)
