from django.db import models
from django.contrib.auth.models import AbstractUser
from .util import phone_number_validator


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, validators=[phone_number_validator])
    email = models.EmailField(blank=True, null=True)  # Email is optional

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='contact_user_set',  # New related_name for this model
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='contact_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='contact_user_permissions',  # New related_name for this model
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='contact_user_permission'
    )

    def __str__(self):
        return self.username


class SpamNumber(models.Model):
    phone_number = models.CharField(max_length=15, unique=True, validators=[phone_number_validator])
    marked_by = models.ForeignKey(User, related_name="marked_spam", on_delete=models.CASCADE)
    marked_count = models.PositiveIntegerField(default=1)
    spam_likelihood = models.FloatField(default=0.1)  # A value between 0 and 1

    def __str__(self):
        return f"Spam: {self.phone_number} marked by {self.marked_by.username} - Likelihood: {self.spam_likelihood}"

    def update_spam_likelihood(self):
        # Update the spam likelihood based on the number of users who marked the number as spam
        self.spam_likelihood = min(1.0, self.marked_count * 0.1)
        self.save()


class Contact(models.Model):
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, validators=[phone_number_validator], default='0000000000')
    name = models.CharField(max_length=255, default='Unknown')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'phone_number'], name='unique_name_phone')
        ]

    def __str__(self):
        return f'{self.name} - {self.phone_number}'
