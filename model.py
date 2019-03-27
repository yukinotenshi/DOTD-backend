from playhouse.shortcuts import model_to_dict
from datetime import datetime
import peewee as pw
import os


db = pw.SqliteDatabase(os.getenv("DATABASE"))


class BaseModel(pw.Model):
    created_at = pw.DateTimeField(default=datetime.now)
    updated_at = pw.DateTimeField(default=datetime.now)

    def to_dict(self):
        return model_to_dict(self)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)

    class Meta:
        database = db


class User(BaseModel):
    username = pw.CharField(unique=True)
    password = pw.CharField()
    level = pw.IntegerField(default=1)
    exp = pw.IntegerField(default=0)

    def to_dict(self):
        return model_to_dict(self, exclude=[User.password])
