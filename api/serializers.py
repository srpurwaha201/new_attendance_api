from rest_framework import serializers
from .models import Student, Subject, Teacher, Section, Attendance, Timetable, Lab
from accounts.models import User
from rest_framework.authtoken.models import Token
from accounts.serializers import UserSerializer
import pickle
import base64

class StudentSerializer(serializers.Serializer):
    user = UserSerializer()
    rollno = serializers.CharField()
    class Meta:
        model = Student
        fields = ['rollno','user','image']


    def create(self, validated_data):
        user_data = validated_data.pop('user')
        email = user_data['email']
        password = user_data.pop('password')
        rollno = validated_data['rollno']

        try:
            if Student.objects.all().filter(rollno=rollno).exists() or User.objects.all().filter(email=email).exists():
                raise Exception("Student already exists")
            user = User.objects.create(**user_data)
            user.set_password(password)
            student = Student.objects.create(user=user, rollno=rollno)
            user.student = student
            user.save()
            student.save()
            token = Token.objects.create(user=user)
            token.save()

        except Exception as e:
            error = {'message': ",".join(e.args) if len(e.args) > 0 else 'Unknown Internal Error'}
            raise serializers.ValidationError(error)


        return student

class TeacherSerializer(serializers.Serializer):
    user = UserSerializer()
    designation = serializers.CharField()
    class Meta:
        model = Teacher
        fields = ['designation','user']


    def create(self, validated_data):
        user_data = validated_data.pop('user')
        email = user_data['email']
        password = user_data.pop('password')
        designation = validated_data['designation']

        try:
            if  User.objects.all().filter(email=email).exists():
                raise Exception("Teacher already exists")
            user = User.objects.create(**user_data)
            user.set_password(password)
            teacher = Teacher.objects.create(user=user, designation=designation)
            user.teacher = teacher
            user.save()
            teacher.save()
            token = Token.objects.create(user=user)
            token.save()
        except Exception as e:
            error = {'message': ",".join(e.args) if len(e.args) > 0 else 'Unknown Internal Error'}
            raise serializers.ValidationError(error)


        return teacher

class SubejctSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    class Meta:
        model = Subject
        fields = ['code', 'name']


class SectionSerializer(serializers.Serializer):
    subject = SubejctSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    slot = serializers.CharField()
    class Meta:
        model = Section
        fields = ['slot', 'subject', 'teacher']

class LabSerializer(serializers.Serializer):
    slot = serializers.CharField()
    subject = SubejctSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    class Meta:
        model = Lab
        fields = ['slot','subject','teacher']

class TimetableSerializer(serializers.Serializer):
    section = SectionSerializer(read_only=True)
    lab = LabSerializer(read_only=True)
    day = serializers.CharField()
    startTime = serializers.TimeField()
    endTime = serializers.TimeField()
    location =  serializers.CharField(max_length = 50)
    category = serializers.CharField(max_length=20)
    class Meta:
        model = Timetable
        fields = ['section','lab', 'day','startTime','endTime', 'location','category']


class AttendanceSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()
    body = serializers.CharField()

    timetable = TimetableSerializer(read_only=True)
    date = serializers.DateField()
    students = StudentSerializer(many = True, read_only=True)


    def create(self, validated_data):
        return Attendance.objects.create(**validated_data)

    #students contain only present students. Total no. of class will be calculated using current date and timetable.
    #total % will be calculated accordingly
    class Meta:
        model = Attendance
        fields = ['timetable', 'date', 'students']