from django.db import models
from accounts.models import User

class Student(models.Model):
    user = models.OneToOneField(User, blank=False, related_name = '+', on_delete=models.CASCADE)
    rollno = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.user.email


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
    slot = models.CharField(primary_key=True, max_length=10)
    subject = models.ForeignKey(Subject, null=False, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student,blank=False)

    def __str__(self):
        return self.slot


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