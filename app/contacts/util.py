from django.core.validators import RegexValidator


# Define a regex validator for phone number
phone_number_validator = RegexValidator(
    regex=r'^\+?[1-9]\d{1,14}$',  # E.164 phone number format
    message="Enter a valid phone number with country code (e.g., +1234567890)."
)