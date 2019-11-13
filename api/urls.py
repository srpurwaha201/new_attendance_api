from django.conf.urls import include, url
from .views import AttendanceView, StudentView, TimetableView, SectionStudentView, TeacherTimetableView, CreateStudentView, CreateTeacherView, RetrieveStudentView, RetrieveTeacherView, TodaysClassesView, UploadStudentImageView, StudentImageView, ImageAttendanceView, ImageAttendanceView2
app_name = "attendances"

urlpatterns = [
    url('attendances/$', AttendanceView.as_view()),
    url('student/$', StudentView.as_view()),
    url('student/profile/create/$', CreateStudentView.as_view()),
    url('teacher/profile/create/$', CreateTeacherView.as_view()),
    url('student/profile/view/$', RetrieveStudentView.as_view()),
    url('teacher/profile/view/$', RetrieveTeacherView.as_view()),
    url('student/timetable/', TimetableView.as_view()),
    url('section_students/$', SectionStudentView.as_view()),
    url('teacher/timetable/$', TeacherTimetableView.as_view()),
    url('teacher/todaysclasses/$',TodaysClassesView.as_view()),
    url('student/image/upload/$',UploadStudentImageView.as_view()),
    url('student/image/$',StudentImageView.as_view()),
    url('attendance/find_faces/$', ImageAttendanceView.as_view()),
url('attendance/find_faces_2/$', ImageAttendanceView2.as_view())
]