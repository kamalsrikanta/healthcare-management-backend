from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Validates registration input and creates the user.

    The email is used as the login identifier (stored as the username) and
    the name is stored in ``first_name``.
    """

    name = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(username__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, attrs):
        user = User(username=attrs["email"], email=attrs["email"], first_name=attrs["name"])
        validate_password(attrs["password"], user=user)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["name"],
            password=validated_data["password"],
        )

    def to_representation(self, instance):
        return {"id": instance.id, "name": instance.first_name, "email": instance.email}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
