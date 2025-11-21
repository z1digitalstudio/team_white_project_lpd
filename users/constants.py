"""
Constants for error messages and validation messages.
Centralized location for all user-related error messages.
"""

# Authentication errors
ERROR_USER_ACCOUNT_DISABLED = "User account is disabled"
ERROR_INVALID_CREDENTIALS = "Invalid credentials"
ERROR_MUST_PROVIDE_CREDENTIALS = "Must provide username and password"

# Registration errors
ERROR_USERNAME_REQUIRED = "Username is required and cannot be empty."
ERROR_USERNAME_TOO_SHORT = "Username must be at least 3 characters long."
ERROR_USERNAME_TOO_LONG = "Username cannot exceed 30 characters."
ERROR_USERNAME_INVALID_CHARS = "Username can only contain letters and numbers. No special characters allowed."

ERROR_EMAIL_REQUIRED = "Email is required and cannot be empty."
ERROR_EMAIL_TOO_SHORT = "Email must be at least 5 characters long."
ERROR_EMAIL_TOO_LONG = "Email cannot exceed 150 characters."

ERROR_FIRST_NAME_REQUIRED = "First name is required and cannot be empty."
ERROR_FIRST_NAME_TOO_SHORT = "First name must be at least 2 characters long."
ERROR_FIRST_NAME_TOO_LONG = "First name cannot exceed 150 characters."

ERROR_LAST_NAME_TOO_SHORT = "Last name must be at least 2 characters long if provided."
ERROR_LAST_NAME_TOO_LONG = "Last name cannot exceed 150 characters."

ERROR_PASSWORD_TOO_SHORT = "Password must be at least 8 characters long."
ERROR_PASSWORD_TOO_LONG = "Password cannot exceed 128 characters."
ERROR_PASSWORDS_DO_NOT_MATCH = "Passwords do not match"

# Success messages
MESSAGE_USER_REGISTERED = "User registered successfully"
MESSAGE_LOGIN_SUCCESSFUL = "Login successful"

# Blog errors (from core/views.py)
ERROR_USER_ALREADY_HAS_BLOG = "User already has a blog"
MESSAGE_USER_ALREADY_HAS_BLOG = "Each user can only have one blog. Use PUT or PATCH to update your existing blog."

