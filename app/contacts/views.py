
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserProfileSerializer, SpamNumberSerializer
from .models import User, SpamNumber, Contact
from .util import phone_number_validator
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Q


# Logger
logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Override global permission settings

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        # Validate incoming data
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"message": "User registered successfully!"},
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError as e:  # Handle duplicate phone number or username
                logger.error(f"IntegrityError during registration: {str(e)}")
                return Response(
                    {"error": "A user with this phone number or username already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:  # Handle unexpected errors
                logger.error(f"Unexpected error during registration: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        if not user or not user.is_authenticated:
            logger.warning("Unauthorized access attempt to user profile.")
            raise NotAuthenticated("User is not authenticated.")

        return user  # Return the logged-in user

    def update(self, request, *args, **kwargs):
        logger.info(f"Profile update requested by user: {request.user.username}")
        return super().update(request, *args, **kwargs)


class MarkSpamView(APIView):
    serializer_class = SpamNumberSerializer
    permission_classes = [IsAuthenticated]

    def validate_phone_number(self, phone_number):
        try:
            phone_number_validator(phone_number)  # Use the existing phone number validator
        except ValidationError:
            raise ValidationError("Enter a valid phone number with country code (e.g., +1234567890).")

    def post(self, request):
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response({"error": "Phone number is required to mark as spam."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the phone number
        try:
            self.validate_phone_number(phone_number)
        except ValidationError as e:
            return Response(
                {"phone_number": "Enter a valid phone number with country code (e.g., +1234567890)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the spam number already exists
        spam_number = SpamNumber.objects.filter(phone_number=phone_number).first()

        if spam_number:
            # Increment the marked_count
            spam_number.marked_count += 1
            spam_number.update_spam_likelihood()
            serializer = SpamNumberSerializer(spam_number)
            return Response({"message": f"Phone number {phone_number} marked as spam.", "data": serializer.data})
        else:
            # Create a new SpamNumber entry if it doesn't exist
            user = request.user
            spam_number = SpamNumber.objects.create(phone_number=phone_number, marked_by=user)
            spam_number.update_spam_likelihood()
            serializer = SpamNumberSerializer(spam_number)
            return Response(
                {"message": f"Phone number {phone_number} marked as spam.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )


class SearchPersonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '').strip()

        if not query:
            return Response({"detail": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Search by name where names start with the query
        results_by_name_start = Contact.objects.filter(
            name__istartswith=query
        ).order_by('name')  # Prioritize names that start with the query

        # Search by name where names contain the query but do not start with it
        results_by_name_contains = Contact.objects.filter(
            name__icontains=query
        ).exclude(name__istartswith=query).order_by('name')

        # Combine the two querysets, ensuring the order is respected
        combined_results = list(results_by_name_start) + list(results_by_name_contains)

        # Prepare the search results
        search_results = []
        search_set = set()
        for result in combined_results:
            user = request.user  # The current authenticated user
            registered_user = User.objects.filter(contacts=result).first()

            if registered_user and user in registered_user.contacts.all():
                email = registered_user.email
            else:
                email = None  # Do not display email if the user is not in the contact list

            spam_likelihood = SpamNumber.objects.filter(phone_number=result.phone_number).first()
            spam_likelihood_value = spam_likelihood.spam_likelihood if spam_likelihood else 0.1

            search_results.append({
                'name': result.name,
                'phone_number': result.phone_number,
                'spam_likelihood': spam_likelihood_value,
                'email': email
            })
            search_set.add((result.name, result.phone_number))

        result_by_phone_number = Contact.objects.filter(phone_number=query)

        # If there's exactly one match (registered user), show that contact
        if result_by_phone_number:
            for contact in result_by_phone_number:
                if (contact.name, contact.phone_number) not in search_set:
                    spam_likelihood = SpamNumber.objects.filter(phone_number=contact.phone_number).first()
                    spam_likelihood_value = spam_likelihood.spam_likelihood if spam_likelihood else 0.1

                    user = request.user  # The current authenticated user
                    registered_user = User.objects.filter(contacts=contact).first()

                    if registered_user and user in registered_user.contacts.all():
                        email = registered_user.email
                    else:
                        email = None  # Do not display email if the user is not in the contact list

                    search_results.append({
                        'name': contact.name,
                        'phone_number': contact.phone_number,
                        'spam_likelihood': spam_likelihood_value,
                        'email': email
                    })

        return Response(search_results, status=status.HTTP_200_OK)
