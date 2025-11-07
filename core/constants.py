"""
Constants and messages used throughout the application.
Centralized for easier maintenance and reusability.
"""

# ============================================================================
# USER MESSAGES
# ============================================================================

# Registration messages
USER_REGISTERED_SUCCESS = 'User registered successfully'

# Login messages
LOGIN_SUCCESS = 'Login successful'
INVALID_CREDENTIALS = 'Invalid credentials'
USER_ACCOUNT_DISABLED = 'User account is disabled'
MUST_PROVIDE_CREDENTIALS = 'Must provide username and password'

# Username validation messages
USERNAME_ALPHANUMERIC_ONLY = (
    'Username can only contain letters and numbers. '
    'No special characters allowed.'
)

# Password validation messages
PASSWORDS_DO_NOT_MATCH = 'Passwords do not match'

# ============================================================================
# BLOG MESSAGES
# ============================================================================

# Blog creation error messages
USER_ALREADY_HAS_BLOG = 'User already has a blog'
BLOG_ONE_PER_USER_MESSAGE = (
    'Each user can only have one blog. '
    'Use PUT or PATCH to update your existing blog.'
)

# Blog title template
BLOG_TITLE_TEMPLATE = 'Blog de {username}'

# ============================================================================
# ERROR KEYS
# ============================================================================

ERROR_KEY = 'error'
MESSAGE_KEY = 'message'

