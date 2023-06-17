from mongoengine import Document, CASCADE
from mongoengine.fields import ListField, StringField, ReferenceField


class Authors(Document):
    full_name = StringField()
    born_date = StringField()
    born_loc = StringField()
    desc = StringField()


class Quotes(Document):
    tags = ListField(StringField())
    author = ReferenceField(Authors, reverse_delete_rule=CASCADE)
    quote = StringField()
