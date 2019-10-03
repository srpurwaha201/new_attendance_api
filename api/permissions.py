from rest_framework import permissions
from .models import Teacher, Student
from accounts.models import User

class AttendancePermission(permissions.BasePermission):

    message = "you are not authorised for marking attendance"

    def has_object_permission(self, request, view, obj):
        user_authorised = obj.section.teacher.user
        token = request.auth
        user_request = User.objects.get(auth_token=token)

        return user_authorised == user_request


class StudentPermission(permissions.BasePermission):
    message = "you are not allowed to view this"

    def has_permission(self, request, view):
        token = request.auth
        user_request = User.objects.get(auth_token=token)
        email = request.GET["email"]
        print (email)
        user_authorized = User.objects.get(email=email)

        return user_authorized == user_request

class TeacherPermission(permissions.BasePermission):

    message = "you are not allowed to view this"

    def has_permission(self, request, view):
        token = request.auth
        user_request = User.objects.get(auth_token=token)
        email = request.GET["email"]
        user_authorized = User.objects.get(email=email)

        return user_authorized == user_request


class ProfilePermission(permissions.BasePermission):
    message = "you are not authorized to do this action"

    def has_permission(self, request, view):
        token = request.auth
        if request.method in permissions.SAFE_METHODS:
            user_request = User.objects.get(auth_token=token)
            email = request.GET["email"]
            user_authorized = User.objects.get(email=email)
            return user_authorized == user_request
        else:
            user_request = User.objects.get(auth_token=token)
            return user_request.is_staff