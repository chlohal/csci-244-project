import uuid
from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    name = models.TextField()
    uuid = models.TextField()

class BlockCategory(models.Model):
    name = models.CharField(max_length = 60, primary_key=True)
    color = models.CharField(max_length = 7)

class BlockType(models.Model):
    category = models.ForeignKey(BlockCategory, on_delete = models.CASCADE)
    name = models.CharField(max_length = 30)
    id = models.CharField(max_length = 164, primary_key=True)

class BlockFlow(models.Model):
    block = models.ForeignKey(BlockType, on_delete = models.CASCADE)
    id = models.CharField(max_length=50, primary_key=True)
    label = models.CharField(max_length=65)
    flow_type = models.CharField(max_length=30)
    is_input = models.BooleanField()


class CanvasToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_url = models.URLField()
    token = models.CharField(max_length=512)

class Flowchart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField()
    last_edit = models.DateTimeField(null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contents = models.JSONField()