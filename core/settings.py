from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file based on DJANGO_ENV


load_dotenv(".env")


SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = str(os.getenv("STATUS_DEBUG")).lower()=="true"
# DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]
CSRF_TRUSTED_ORIGINS = [str(os.getenv("CSRF_TRUSTED_ORIGINS"))]


# Application definition

INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_prometheus',
    
    # app register
    'menu.apps.MenuConfig',
    'user.apps.UserConfig',
    'home.apps.HomeConfig',
    'menu.mapel.apps.MapelConfig',
    'menu.pembayaran.apps.PembayaranConfig',
    'menu.modul.apps.ModulConfig',
    'menu.ujian.apps.UjianConfig',
    'menu.nilai.apps.NilaiConfig',
    'menu.levelstudy.apps.LevelstudyConfig',
    
    'django_ckeditor_5',
    
    'health_check',                            
    'health_check.db',
    'health_check.contrib.migrations',
    'health_check.contrib.celery',              
    'health_check.contrib.celery_ping',     
    'health_check.contrib.redis',
    
    
]
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.utils.get_request.RequestMiddleware',
    'core.utils.middleware.PreventMultipleLoginsMiddleware',
    'core.utils.middleware.ValidateProfileMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'menu.pembayaran.context_processor.transaksi',
                'user.context_processor.get_foto_profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
IS_DOCKER = str(os.getenv("IS_DOCKER")).lower()=="true"

if IS_DOCKER:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', 
            'NAME': os.getenv("MYSQL_DATABASE"),
            'USER': 'root',
            'PASSWORD': os.getenv('MYSQL_ROOT_PASSWORD'),
            'HOST': 'mysql_container',
            'PORT': '3306',
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [('redis_container', '6379')],
            },
        },
    }
    CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://'+'redis_container'+':6379/1',
        'OPTIONS': {
            
            }
        }
    }
    CELERY_BROKER_URL = 'redis://'+'redis_container'+':6379/2'
    CELERY_RESULT_BACKEND = 'redis://'+'redis_container'+':6379/2'
    REDIS_URL = 'redis://'+'redis_container'+':6379'
    
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', 
            'NAME': 'bimbel',
            'USER': 'root',
            'PASSWORD': 'mysqladmin',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1","6379")],
            },
        },
    }
    CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            }
        }
    }
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
    REDIS_URL = 'redis://127.0.0.1:6379'
    


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'id'

TIME_ZONE = 'Asia/Makassar'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR/'locale']


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'nginx/staticfiles'
CKEDITOR_BASEPATH = STATIC_ROOT
STATICFILES_DIRS = [
    BASE_DIR/'static',    
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "user.Users"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
SERVER_EMAIL = os.getenv('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER')

MIDTRANS = {
    'MERCHANT_ID': os.getenv('MERCHANT_ID'),
    'IS_PRODUCTION': str(os.getenv('IS_PRODUCTION')).lower()=="true",
    'SERVER_KEY': os.getenv('SERVER_KEY'),
    'CLIENT_KEY': os.getenv('CLIENT_KEY'),
}

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

PASSWORD_RESET_TIMEOUT_DAYS = 7

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # Remove the 'file' handler if you don't want to save logs
        # 'file': {
        #     'class': 'logging.FileHandler',
        #     'filename': os.path.join(BASE_DIR, 'django.log'),
        #     'formatter': 'verbose',
        # },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

handler404 = 'core.views.custom_404_handler'
handler500 = 'core.views.custom_500_handler'
CSRF_FAILURE_VIEW ="core.views.csrf_failure"
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 300 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 300 MB
LOGIN_URL='/users/masuk/'

customColorPalette = [
        {
            'color': 'hsl(4, 90%, 58%)',
            'label': 'Red'
        },
        {
            'color': 'hsl(340, 82%, 52%)',
            'label': 'Pink'
        },
        {
            'color': 'hsl(291, 64%, 42%)',
            'label': 'Purple'
        },
        {
            'color': 'hsl(262, 52%, 47%)',
            'label': 'Deep Purple'
        },
        {
            'color': 'hsl(231, 48%, 48%)',
            'label': 'Indigo'
        },
        {
            'color': 'hsl(207, 90%, 54%)',
            'label': 'Blue'
        },
    ]

# CKEDITOR_5_CUSTOM_CSS = 'path_to.css' # optional
# CKEDITOR_5_FILE_STORAGE = "path_to_storage.CustomStorage" # optional
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'codeBlock', 'sourceEditing',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor',  'removeFormat',
                    'insertTable',],
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'