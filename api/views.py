from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .permissions import AttendancePermission, StudentPermission, TeacherPermission, ProfilePermission
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
import datetime
from datetime import date

class AttendanceView(APIView):
    permission_classes = [IsAuthenticated, AttendancePermission]
    def post(self, request):
        try:
            # timetableid = request.data.get('timetableid')
            # timetable = Timetable.objects.get(id=timetableid)
            date = request.data.get('date')
            year, month, day = (int(i) for i in date.split('-'))
            weekday = datetime.date(year, month, day).strftime("%A") 
            rollnos = request.data.get('rollnos')
            lab = request.data.get('lab')
            slot = request.data.get('slot')

            students = []
            for r in rollnos:
                students.append(Student.objects.get(rollno=r))

            if lab=='True':
                subslot = request.data.get('subslot')
                timetable = Timetable.objects.filter(lab__slot = slot).filter(lab__subslot=subslot).filter(day=weekday)[0]
                attendance, _ = Attendance.objects.get_or_create(timetable=timetable, date=date, lab=True)
            else:
                timetable = Timetable.objects.filter(section__slot = slot).filter(day=weekday)[0]
                attendance, _ = Attendance.objects.get_or_create(timetable=timetable, date=date, lab = False)
            # print (self.check_object_permissions(request, timetable))
            # print(rollnos)
            
            # print(attendance)
            for s in students:
                attendance.students.add(s)
            attendance.save()

        except PermissionDenied as e:
            return Response({"detail": str(e)})

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
        user = User.objects.get(email=self.request.GET["email"])
        obj = get_object_or_404(queryset, user=user)
        return obj

class RetrieveTeacherView(RetrieveAPIView):
    queryset = Teacher.objects.all()
    permission_classes = [IsAuthenticated, ProfilePermission]
    serializer_class = TeacherSerializer
    model = Teacher

    def get_object(self):
        queryset = self.get_queryset()
        user = User.objects.get(email=self.request.GET["email"])
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
                del i['teacher']
                total = len(Attendance.objects.filter(lab=False).filter(timetable__section__slot=i['slot']))
                present = len(student.attendance_set.all().filter(lab=False).filter(timetable__section__slot=i['slot']))
                i['total'] = total
                i['present'] = present
                lab = student.lab_set.all().filter(slot=i['slot'])
                if len(lab)!=0:
                    lab = lab[0]
                    i['total']+=len(Attendance.objects.filter(timetable__lab__slot=lab.slot).filter(timetable__lab__subslot=lab.subslot))
                    i['present']+=len(student.attendance_set.all().filter(timetable__lab__slot=lab.slot).filter(timetable__lab__subslot=lab.subslot))
        except Exception as e:
            print ("error occured in StudentView", e)
            return Response({"status": "0", "error": "internal error occured", "exception": e})

        return Response({"status": "1", "Student": studentserializer.data, "Sections": sectionserializer.data})

class TimetableView(APIView):
    permission_classes = [IsAuthenticated, StudentPermission]
    def get(self, request):
        try:
            email = request.GET["email"]
            student = Student.objects.get(user__email=email)
            sections = student.section_set.all()
            response = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}
            for i in sections:
                # print(i)
                timetables = i.timetable_set.all()
                timetableserializer = TimetableSerializer(timetables, many=True)
                for j in timetableserializer.data:
                    # print(j)
                    j['type']='section'
                    response[j['day']].append(j)
            
            labs = student.lab_set.all()
            for i in labs:
                # print(i)
                timetables = i.timetable_set.all()
                timetableserializer = TimetableSerializer(timetables, many=True)
                for j in timetableserializer.data:
                    # print(j)
                    # del j['lab']['section']
                    j['type']='lab'
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
            email = request.GET["email"]
            teacher = Teacher.objects.get(user__email=email)
            section = teacher.section_set.all().filter(slot=request.GET["slot"])[0]
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
            email = request.GET["email"]
            teacher = Teacher.objects.get(user__email=email)
            sections = teacher.section_set.all()
            response = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}
            for i in sections:
                # print(i)
                timetables = i.timetable_set.all()
                timetableserializer = TimetableSerializer(timetables, many=True)
                for j in timetableserializer.data:
                    del j['section']['teacher']
                    response[j['day']].append(j)

            labs = teacher.lab_set.all()
            for i in labs:
                # print(i)
                timetables = i.timetable_set.all()
                timetableserializer = TimetableSerializer(timetables, many=True)
                for j in timetableserializer.data:
                    # print(j)
                    # del j['lab']['section']
                    j['type']='lab'
                    response[j['day']].append(j)

            for _, value in response.items():
                value.sort(key=lambda item:item['startTime'])
            response["status"] = "1"
        except Exception as e:
            print ("error occured in TeacherTimeTableView", e)
            return Response({"status": "0", "error": "internal error occured"})

        return Response(response)

class TodaysClassesView(APIView):
    permission_classes = [IsAuthenticated, TeacherPermission]
    def get(self, request):
        try:
            email = request.GET['email']
            days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            # todaysday = days[datetime.now().day]
            todaysday='Monday'
            classes = []
            teacher = Teacher.objects.get(user__email=email)
            sections = teacher.section_set.all()
            for sec in sections:
                timetables = sec.timetable_set.all().filter(day=todaysday)
                timetableserializer = TimetableSerializer(timetables, many=True)
                # del sec['teacher']
                for t in timetableserializer.data:
                    del t['section']['teacher'] 
                    classes.append(t)
            
            response = {}
            response['classes']=classes
            response['date'] = str(date.today())
            response['status']='1'
        except Exception as e:
            print ("error occured in TodaysClassesView", e)
            return Response({"status": "0", "error": "internal error occured"})
        return Response(response)




