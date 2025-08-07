# Development-specific settings
# Inherit from main settings
from .settings import *

# Override for development
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Disable HTTPS redirects for development
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

# Disable secure cookies for development  
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable HSTS for development
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

print("🚀 Running in DEVELOPMENT mode - HTTP only!")
