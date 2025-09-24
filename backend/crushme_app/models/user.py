"""
User authentication models based on the signin_signon_feature and gym_project repositories
Extends Django's AbstractUser for custom authentication with JWT support
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import random
import string


class UserManager(BaseUserManager):
    """
    Custom user manager to handle user creation with email as the unique identifier.
    Based on signin_signon_feature and gym_project pattern
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and returns a regular user with the given email and password.

        Args:
            email (str): The email of the user.
            password (str, optional): The password for the user. Defaults to None.
            **extra_fields: Additional fields for the user model.

        Raises:
            ValueError: If the email is not provided.

        Returns:
            User: The created user instance.
        """
        if not email:
            raise ValueError('The email must be defined')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with the given email and password.

        Args:
            email (str): The email of the superuser.
            password (str, optional): The password for the superuser. Defaults to None.
            **extra_fields: Additional fields for the superuser model.

        Raises:
            ValueError: If is_staff or is_superuser is not set to True.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model extending AbstractUser. Uses email as the unique identifier instead of username.
    Based on signin_signon_feature and gym_project implementation
    
    Attributes:
        email (EmailField): The unique email of the user.
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.
    """
    # Remove the username, groups, and user_permissions fields
    username = None
    groups = None
    user_permissions = None
    
    # Use email as the unique identifier
    email = models.EmailField(unique=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=60, verbose_name="First Name")
    last_name = models.CharField(max_length=60, verbose_name="Last Name")

    # Set email as the username field and define required fields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Use the custom user manager
    objects = UserManager()

    def __str__(self):
        """
        String representation of the User instance.
        
        Returns:
            str: The email of the user.
        """
        return self.email
    
    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class PasswordCode(models.Model):
    """
    Model to store password reset codes associated with a user.
    Based on signin_signon_feature implementation
    
    Attributes:
        user (ForeignKey): A foreign key linking the code to a user.
        code (CharField): A 6-digit code used for password reset.
        created_at (DateTimeField): Timestamp of when the code was created.
        used (BooleanField): Flag to indicate if the code has been used.
    """
    # Link each password code to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_codes')
    
    # The reset code, restricted to a maximum length of 6 digits
    code = models.CharField(
        max_length=6,
        validators=[RegexValidator(regex='^\d{6}$', message='Code must be 6 digits', code='invalid_code')]
    )
    
    # Timestamp of when the password code was created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Flag to indicate whether the code has been used
    used = models.BooleanField(default=False)

    def __str__(self):
        """
        String representation of the PasswordCode instance.
        
        Returns:
            str: The user's email and the password reset code.
        """
        return f'{self.user.email} - {self.code}'

    class Meta:
        """
        Meta options for the PasswordCode model.
        
        Attributes:
            ordering (list): Default ordering for querysets.
            verbose_name (str): Human-readable singular name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
        """
        ordering = ['-created_at']
        verbose_name = 'Password Code'
        verbose_name_plural = 'Password Codes'
