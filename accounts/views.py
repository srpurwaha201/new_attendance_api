# Create your views here.
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from api.serializers import TeacherSerializer, StudentSerializer, UserSerializer
from rest_framework.response import Response
from api.models import Student,Teacher


@permission_classes([AllowAny])
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        username, password = request.data.get('email'), request.data.get('password')
        user = authenticate(username=username, password=password)
        response = {"data": None,
                    "token": None,
                    "type": None}
        if user:
            if user.teacher:
                teacher = Teacher.objects.get(user=user)
                teacher_data = TeacherSerializer(teacher).data
                response["data"] = teacher_data
                response["type"] = "teacher"
            elif user.student:
                student = Student.objects.get(user=user)
                student_data = StudentSerializer(student).data
                response["data"] = student_data
                response["type"] = "student"
            else:
                user_data = UserSerializer(user).data
                response["data"] = user_data
                response["type"] = "admin"

            token = Token.objects.get(user=user).key
            response["token"] = token
            return Response(response)
        else:
            return Response({"message": "Invalid login credentials"})





