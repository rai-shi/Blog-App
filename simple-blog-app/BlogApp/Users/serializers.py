from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]

        # password will not be shown
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_password(self, value):
            try:
                # Django password validators (minimum length, complexity, etc.)
                validate_password(value)  
            except Exception as e:
                raise serializers.ValidationError(str(e))
            return value
    
    # create new hashed instance of password 
    def create(self, validate_data):
        password = validate_data.pop("password", None)
        instance = self.Meta.model(**validate_data)
        if password is not None:
            # hashing the password with sha256
            instance.set_password(password)
        instance.save()
        return instance 
    
    # updating password with hashing
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)
    