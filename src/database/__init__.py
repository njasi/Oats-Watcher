# make the connection to the tinydb here, import the tables from here
from tinydb import TinyDB

db = TinyDB("data/db.json", indent=4)

User = db.table("user")
History = db.table("history")
