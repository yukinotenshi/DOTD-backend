import dotenv

dotenv.load_dotenv()

from model import *

db.connect()
db.create_tables([User])
db.close()
