from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .permissions import AttendancePermission, StudentPermission, TeacherPermission, ProfilePermission
from django.shortcuts import get_object_or_404

class AttendanceView(APIView):
    permission_classes = [IsAuthenticated, AttendancePermission]
    def post(self, request):
        try:
            timetableid = request.data.get('timetableid')[0]
            timetable = Timetable.objects.get(id=timetableid)
            date = request.data.get('date')
            rollnos = request.data.get('rollnos')
            self.check_object_permissions(request,timetable)
            print(rollnos)
            attendance = Attendance.objects.create(timetable = timetable, date = date)
            for r in rollnos:
                attendance.students.add(Student.objects.get(rollno = r))
            attendance.save()

        except Exception as e:
            print ("error while saving atendance",e)
            return Response({"status": "0", "error": "Internal error occured"})

        return Response({"status": "1"})

class CreateStudentView(CreateAPIView):
    permission_classes = [IsAuthenticated, ProfilePermission]
    serializer_class = StudentSerializer
    model = Student

class CreateTeacherView(CreateAPIView):
    permission_classes = [IsAuthenticated, ProfilePermission]
    serializer_class = TeacherSerializer
    model = Teacher

class RetrieveStudentView(RetrieveAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated, ProfilePermission]
    serializer_class = StudentSerializer
    model = Student

    def get_object(self):
        queryset = self.get_queryset()
        user = User.objects.get(email=self.request.data.get('email'))
        obj = get_object_or_404(queryset, user=user)
        return obj

class RetrieveTeacherView(RetrieveAPIView):
    queryset = Teacher.objects.all()
    permission_classes = [IsAuthenticated, ProfilePermission]
    serializer_class = TeacherSerializer
    model = Teacher

    def get_object(self):
        queryset = self.get_queryset()
        user = User.objects.get(email=self.request.data.get('email'))
        obj = get_object_or_404(queryset, user=user)
        return obj

class StudentView(APIView):
    permission_classes = [IsAuthenticated, StudentPermission]
    def get(self, request):
        # print("roll no is -------------> ",request.data.get('rollno'))
        # rollno = request.data.get('rollno')
        try:
            email = request.GET["email"]
            student = Student.objects.get(user__email=email)
            # print("studet is ------------------------>",student.name)
            sections = student.section_set.all()
            studentserializer = StudentSerializer(student)
            sectionserializer = SectionSerializer(sections, many=True)
            for i in sectionserializer.data:
                total = len(Attendance.objects.filter(timetable__section__slot=i['slot']))
                present = len(student.attendance_set.all().filter(timetable__section__slot=i['slot']))
                i['total'] = total
                i['present'] = present
        except Exception as e:
            print ("error occured in StudentView", e)
            return Response({"status": "0", "error": "internal error occured"})

        return Response({"status": "1", "Student": studentserializer.data, "Sections": sectionserializer.data})

class TimetableView(APIView):
    permission_classes = [IsAuthenticated, StudentPermission]
    def get(self, request):
        try:
            email = request.GET['email']
            student = Student.objects.get(user__email=email)
            sections = student.section_set.all()
            response = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}
            for i in sections:
                # print(i)
                timetables = i.timetable_set.all()
                timetableserializer = TimetableSerializer(timetables, many=True)
                for j in timetableserializer.data:
                    # print(j)
                    response[j['day']].append(j)

            for _, value in response.items():
                value.sort(key=lambda item:item['startTime'])
                response["status"] = "1"
        except Exception as e:
            print("error inTimeTableView", e)
            return Response({"status": "0", "error": "internal error occured"})

        return Response(response)

class SectionStudentView(APIView):
    permission_classes = [IsAuthenticated, TeacherPermission]
    def get(self, request):
        try:
            email = request.GET['email']
            teacher = Teacher.objects.get(email=email)
            section = teacher.section_set.all().filter(slot=request.GET['slot'])[0]
            sectionserializer = SectionSerializer(section)
            students = section.students.all()
            studentsserializer = StudentSerializer(students, many=True)
        except Exception as e:
            print ("error occured in SectionStudentView",e)
            return Response({"status": "0", "error": "internal server error occured"})

        return Response({"status": "1", "Section": sectionserializer.data, "Students": studentsserializer.data})


class TeacherTimetableView(APIView):
    permission_classes = [IsAuthenticated, TeacherPermission]
    def get(self, request):
        try:
            email = request.GET['email']
            teacher = Teacher.objects.get(email=email)
            sections = teacher.section_set.all()
            response = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}
            for i in sections:
                # print(i)
                timetables = i.timetable_set.all()
                timetableserializer = TimetableSerializer(timetables, many=True)
                for j in timetableserializer.data:
                    del j['section']['teacher']
                    response[j['day']].append(j)

            for _, value in response.items():
                value.sort(key=lambda item:item['startTime'])
            response["status"] = "1"
        except Exception as e:
            print ("error occured in TeacherTimeTableView", e)
            return Response({"status": "0", "error": "internal error occured"})

        return Response(response)