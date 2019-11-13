from django.db import models
from accounts.models import User
from django.utils.safestring import mark_safe
from .facerecog import get_embedding
import pickle
import base64
from django.db.models.signals import post_save
from django.dispatch import receiver




class Student(models.Model):
    user = models.OneToOneField(User, blank=False, related_name = '+', on_delete=models.CASCADE)
    rollno = models.CharField(max_length=50, primary_key=True)
    image = models.ImageField(blank=True, null=True)
    embedding = models.BinaryField(blank = True, null = True)

    def __str__(self):
        return self.user.email

    # def image_tag(self):
    #     from django.utils.html import escape
    #     return u'<img src="%s" />' % escape(self.image.url)
    # image_tag.short_description = 'Image'
    # image_tag.allow_tags = True

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.image))

    image_tag.short_description = 'Image'

@receiver(post_save, sender=Student, dispatch_uid="update_stock_count")
def save_embedding(sender, instance, created, **kwargs):
    if created:
        embedding = get_embedding(instance.image.path)
        np_bytes = pickle.dumps(embedding)
        np_base64 = base64.b64encode(np_bytes)
        instance.embedding = np_base64
        instance.save()

class Teacher(models.Model):
    user = models.OneToOneField(User, blank=False, related_name = '+', on_delete=models.CASCADE)
    designation = models.CharField(max_length=50)

    def __str__(self):
        return self.user.email

class Subject(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return (self.name+"-"+self.code)


class Section(models.Model):
    #will include slot like CO402-P
    slot = models.CharField(primary_key=True, max_length=10)
    subject = models.ForeignKey(Subject, null=False,on_delete=models.CASCADE)
    students = models.ManyToManyField(Student,blank=False)
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE)

    def __str__(self):
        return self.slot

class Lab(models.Model):
    slot = models.CharField(max_length=10)
    subslot = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, null=False, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student,blank=False)
    
    class Meta:
        unique_together = ('slot', 'subslot')

    def __str__(self):
        return self.slot+'-'+self.subslot


class Timetable(models.Model):
    Mon = "Monday"
    Tue = "Tuesday"
    Wed = "Wednesday"
    Thur = "Thursday"
    Fri = "Friday"
    DAY_CHOICES = [
        (Mon,"Monday"),
        (Tue,"Tuesday"),
        (Wed,"Wednesday"),
        (Thur,"Thursday"),
        (Fri,"Friday")
    ]
    section = models.ForeignKey(Section, null=True,blank = True,on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab,null=True, blank=True, on_delete=models.CASCADE)
    day = models.CharField(max_length=20, choices = DAY_CHOICES, default=Mon)
    startTime = models.TimeField()
    endTime = models.TimeField()
    location = models.CharField(max_length = 50)
    L = "lab"
    S = "section"
    CATEGORY_CHOICES = [(L, "lab"),(S,"section")]
    category = models.CharField(max_length=20, choices = CATEGORY_CHOICES, default=S)

    def __str__(self):
        if self.section is None:
            return "Lab"+"-"+str(self.lab)+"-"+self.day
        else :
            return str(self.section)+"-"+self.day

class Attendance(models.Model):
    timetable = models.ForeignKey(Timetable,on_delete=models.CASCADE)
    date = models.DateField()
    #students contain only present students. Total no. of class will be calculated using current date and timetable.
    #total % will be calculated accordingly
    students = models.ManyToManyField(Student)
    lab = models.BooleanField(default=False)

    def __str__(self):
        if self.lab==True:
            return str(self.timetable.lab)+"-"+str(self.date)
        else:
            return str(self.timetable.section)+"-"+str(self.date)
