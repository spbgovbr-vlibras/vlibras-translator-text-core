from pymodm import fields
from pymodm import MongoModel


class Videos(MongoModel):
    gloss = fields.CharField(required=True)
    uid = fields.CharField(required=True)
    path = fields.CharField()
    size = fields.IntegerField()
    duration = fields.IntegerField()
    status = fields.CharField(required=True)
    requester = fields.CharField(required=True)
    createdAt = fields.DateTimeField()
    updatedAt = fields.DateTimeField()

    class Meta:
        final = True

class StatusVideosTranslations(MongoModel):
    status = fields.CharField(required=True)
    createdAt = fields.DateTimeField()
    updatedAt = fields.DateTimeField()

    class Meta:
        final = True
