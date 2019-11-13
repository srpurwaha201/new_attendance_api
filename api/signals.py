from  .models import Student

from .facerecog import get_embedding
import pickle
import base64
from .models import Student
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Student, dispatch_uid='example_method')
def save_embedding(sender, student, **kwargs):
    if student.image not None and student.embedding==None
        embedding = get_embedding(student.image.path)
        np_bytes = pickle.dumps(embedding)
        np_base64 = base64.b64encode(np_bytes)
        if student.embedding!= np_base64
            student.embedding = np_base64
            student.save

