import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load file .env
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.vercel.app', '.railway.app']

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.sites',
    
    
    # Third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.twitter',  # Twitter/X
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local apps
    'apps.core',
    'apps.games',
    'apps.users',
    'apps.orders',
]

JAZZMIN_SETTINGS = {
    "site_title": "Web Topup Admin",
    "site_header": "Web Topup",
    "site_brand": "Web Topup",
    "site_logo": None,
    "welcome_sign": "Selamat Datang di Admin Panel Web Topup",
    "copyright": "Web Topup © 2026",
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Lihat Website", "url": "/", "new_window": True},
    ],
    
    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # Icons (Font Awesome 5)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "games.Game": "fas fa-gamepad",
        "games.GameCategory": "fas fa-tags",
        "games.GameItem": "fas fa-diamond",
        "orders.Order": "fas fa-shopping-cart",
        "users.CustomUser": "fas fa-user-circle",
    },
    
    # Custom Links
    "custom_links": {
        "orders": [{
            "name": "Laporan Penjualan", 
            "url": "admin:laporan-penjualan", 
            "icon": "fas fa-chart-line",
            "permissions": ["orders.view_order"]
        }]
    },
    
    # UI Customizer
    "show_ui_builder": True,
    
    # Default Theme
    "theme": "darkly",  # darkly, flatly, sandstone, etc
}

JAZZMIN_UI_THEMES = {
    "darkly": "https://bootswatch.com/5/darkly/bootstrap.min.css",
    "flatly": "https://bootswatch.com/5/flatly/bootstrap.min.css",
    "sandstone": "https://bootswatch.com/5/sandstone/bootstrap.min.css",
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# Coba pakai SQLite dulu untuk testing, nanti ganti PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Kalau mau pake PostgreSQL, uncomment ini:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DATABASE_NAME'),
#         'USER': os.getenv('DATABASE_USER'),
#         'PASSWORD': os.getenv('DATABASE_PASSWORD'),
#         'HOST': os.getenv('DATABASE_HOST'),
#         'PORT': os.getenv('DATABASE_PORT'),
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'id-id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

# Login URLs
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'games:list'
LOGOUT_REDIRECT_URL = 'games:list'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

CART_SESSION_ID = 'cart'

SITE_ID = 1

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    #'facebook': {
     #   'METHOD': 'oauth2',
      #  'SCOPE': ['email', 'public_profile'],
       # 'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
       # 'FIELDS': [
        #    'id',
        #    'email',
        #    'name',
         #   'first_name',
         #   'last_name',
         #   'verified',
         #   'locale',
         #   'timezone',
          #  'link',
          #  'gender',
        #],
        #'EXCHANGE_TOKEN': True,
       # 'LOCALE_FUNC': lambda request: 'id_ID',
        #'VERIFIED_EMAIL': False,
        #'VERSION': 'v12.0',
   # },
}

# Allauth settings
#ACCOUNT_EMAIL_REQUIRED = True
#ACCOUNT_USERNAME_REQUIRED = True
#ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
LOGIN_REDIRECT_URL = 'games:list'
ACCOUNT_LOGOUT_REDIRECT_URL = 'games:list'

ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# Midtrans Configuration
MIDTRANS_MERCHANT_ID = os.getenv('MIDTRANS_MERCHANT_ID')
MIDTRANS_CLIENT_KEY = os.getenv('MIDTRANS_CLIENT_KEY')
MIDTRANS_SERVER_KEY = os.getenv('MIDTRANS_SERVER_KEY')
MIDTRANS_IS_PRODUCTION = os.getenv('MIDTRANS_IS_PRODUCTION') == 'True'
MIDTRANS_SNAP_URL = 'https://app.sandbox.midtrans.com/snap/v2/vtweb/' if not MIDTRANS_IS_PRODUCTION else 'https://app.midtrans.com/snap/v2/vtweb/'


# ===== PRODUCTION SETTINGS FOR RAILWAY =====
# Security settings for production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '.vercel.app',
        '.railway.app',
        'moba-topup.up.railway.app',
        os.environ.get('RAILWAY_PUBLIC_DOMAIN', ''),
        'healthcheck.railway.app',
        ]
         # Trusted origins untuk CSRF
    CSRF_TRUSTED_ORIGINS = [
        'https://*.railway.app',
        'https://' + os.environ.get('RAILWAY_PUBLIC_DOMAIN', ''),
    

    ]

# Database configuration for Railway
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True  # Tambahkan untuk Railway
    )
    print("Using PostgreSQL database from Railway")
else:
    print("Using SQLite database")
    # Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }