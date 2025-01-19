from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
from .models import User, SpamNumber, Contact


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False},
        }

    def validate_password(self, value):
        validate_password(value)  # Use Django's built-in password validator
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'email']
        read_only_fields = ['username', 'phone_number']  # Prevent updates to these fields


class SpamNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamNumber
        fields = ['phone_number', 'marked_by', 'marked_count', 'spam_likelihood']

    def validate_phone_number(self, value):
        """Custom validation for phone number."""
        # Ensure phone number is in a valid format, e.g., digits only, and no special characters
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value


class SearchResultSerializer(serializers.ModelSerializer):
    spam_likelihood = serializers.FloatField()

    class Meta:
        model = Contact
        fields = ['name', 'phone_number', 'spam_likelihood']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'phone_number']

