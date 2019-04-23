from playhouse.migrate import SqliteDatabase, SqliteMigrator, IntegerField, migrate
import dotenv
import os

dotenv.load_dotenv()
db = SqliteDatabase(os.getenv("DATABASE"))

migrator = SqliteMigrator(database=db)
migrate(
    migrator.add_column("user", "level", IntegerField(default=1)),
    migrator.add_column("user", "exp", IntegerField(default=0)),
)
