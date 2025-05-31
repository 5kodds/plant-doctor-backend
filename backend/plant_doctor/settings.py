"""
Django settings for plant_doctor project.
"""
import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- START: Load .env file for local development in Codespaces ---
# This should be near the top, after BASE_DIR is defined.
# Ensure .env is in your .gitignore!
dotenv_path = BASE_DIR / '.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print("🟢 (settings.py) .env file loaded.")
else:
    print("🟡 (settings.py) .env file not found, relying on system environment variables.")
# --- END: Load .env file ---

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    print("🔴 WARNING: (settings.py) DJANGO_SECRET_KEY environment variable not found. Using default (INSECURE for prod).")
    SECRET_KEY = 'your_temporary_insecure_development_key_make_sure_this_is_not_used_in_prod_or_vercel'

# DEBUG mode
# For Vercel, set DEBUG=False via an environment variable.
# For local Codespaces dev, if DEBUG is not in .env, it defaults to True here for convenience.
DEBUG_ENV = os.environ.get('DEBUG', 'False') # Default to 'True' string if not set
DEBUG = DEBUG_ENV.lower() in ('true', '1', 't')
if DEBUG:
    print("🟡 (settings.py) DEBUG mode is ON.")
else:
    print("🟢 (settings.py) DEBUG mode is OFF.")


# ALLOWED_HOSTS
# If DEBUG is False, Django requires this to be set.
# For Vercel, you'll add your Vercel app domain here via an environment variable.
# Example: ALLOWED_HOSTS_ENV="plant-doctor-backend.vercel.app,localhost,127.0.0.1"
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]
    print(f"🟢 (settings.py) ALLOWED_HOSTS loaded from env: {ALLOWED_HOSTS}")
elif DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*'] # More permissive for local debug
    print(f"🟡 (settings.py) DEBUG is ON, ALLOWED_HOSTS set to: {ALLOWED_HOSTS}")
else:
    ALLOWED_HOSTS = [] # Must be set in Vercel env if DEBUG=False
    print("🔴 WARNING: (settings.py) DEBUG is OFF and ALLOWED_HOSTS is not set via environment variable. This will fail on Vercel.")


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',      # <-- ADDED for Cross-Origin Resource Sharing
    'analyzer',         # <-- ADDED your application
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # <-- ADDED: Should be high up, especially before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'plant_doctor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'plant_doctor.wsgi.application'


# Database
# Configured to use DATABASE_URL from environment variables (for Supabase on Vercel)
# Falls back to SQLite for local development if DATABASE_URL is not set in .env
# Make sure 'dj_database_url' is in your requirements.txt

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True) # ssl_require=True often needed for cloud DBs
    }
    print("🟢 (settings.py) Using DATABASE_URL from environment for database.")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("🟡 (settings.py) DATABASE_URL not found, falling back to local SQLite. (NOT for Vercel production)")


# Password validation
# ... (your existing AUTH_PASSWORD_VALIDATORS) ...
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# ... (your existing I18N settings) ...
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
# For Vercel, you might need to configure STATIC_ROOT and run collectstatic,
# or use a service like WhiteNoise if Django itself is serving static files in prod (less common on Vercel).
# Vercel often handles static files for the frontend separately if it's a distinct Vercel project.
# If Django needs to serve its own admin static files via Vercel:
STATIC_ROOT = BASE_DIR / "staticfiles" # Vercel will collect static files here during build


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG # Allow all origins if DEBUG is True (for local dev)
                               # If DEBUG is False (Vercel prod), you'll need to set specific origins
CORS_ALLOWED_ORIGINS = []
if not DEBUG and 'CORS_ALLOWED_ORIGINS_ENV' in os.environ:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS_ENV').split(',')]
    print(f"🟢 (settings.py) CORS_ALLOWED_ORIGINS loaded from env: {CORS_ALLOWED_ORIGINS}")
elif not DEBUG:
    print("🔴 WARNING: (settings.py) DEBUG is OFF and CORS_ALLOWED_ORIGINS_ENV is not set. CORS might block frontend.")


# Gemini API Key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("🔴 WARNING: (settings.py) GOOGLE_API_KEY environment variable not found.")