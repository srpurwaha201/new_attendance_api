from rest_framework import serializers
from api.models import User



class UserSerializer(serializers.HyperlinkedModelSerializer):
    first_name = serializers.CharField(allow_blank = False)
    last_name = serializers.CharField(allow_blank = False)
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only = True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

